import difflib

import pandas as pd
from pymongo import MongoClient, ReplaceOne

DATA_DIR = r"C:\Users\joshu\OneDrive\Desktop\Joshua\cs\etl\datasets"
NRAUS_FILE = rf"{DATA_DIR}\2020_NRAUS_Australia_New_Zealand_Food_Category_Cost_Dataset.xlsx"
NUTRIENT_FILE = rf"{DATA_DIR}\AUSNUT 2023 - Food nutrient profiles.xlsx"
DETAILS_FILE = rf"{DATA_DIR}\AUSNUT-2023-Food-details-4.xlsx"
MATCH_FILE = rf"{DATA_DIR}\AUSNUT-2023-to-2011-13-Matching-file-1.xlsx"

MACRO_COLS = ["energy_kj", "protein_g", "fat_g", "carbs_g", "fibre_g", "sugars_g"]

MANUAL_MATCHES = {
    "11805001": "Breakfast cereal, beverage, chocolate flavour, added vitamins & minerals",
    "11805004": "Breakfast cereal, beverage, non-chocolate flavours, added vitamins & minerals",
    "11501016": "Soft drink, fruit flavours",
    "11401008": "Cordial base, fruit juice/flavours",
    "15202002": "Mussel, cooked",
    "15202003": "Mussel, cooked",
    "18102008": "Lamb, steak, boneless, lean, raw",
    "18103005": "Pork, steak, lean, raw",
    "18103037": "Pork, chop, no fat removed, raw",
    "27201008": "Jam, berry",
    "23504003": "Dip, cucumber & yoghurt, commercial",
    "13304014": "Muffin, cake-style, chocolate or choc-chip",
    "13304016": "Muffin, cake-style, citrus",
}

def token_sort(text):
    return " ".join(sorted(str(text).lower().replace(",", " ").split()))


def best_fuzzy_match(code, name_2011, candidates):
    target = token_sort(name_2011)
    for prefix_len in (5, 3):
        pool = candidates[candidates["survey_id"].str[:prefix_len] == code[:prefix_len]]
        if pool.empty:
            continue
        scores = pool["ausnut_name"].map(
            lambda name: difflib.SequenceMatcher(None, target, token_sort(name)).ratio()
        )
        best = scores.idxmax()
        if scores[best] >= 0.6:
            return pool.at[best, "food_key"], round(float(scores[best]), 2)
    return None, 0.0


def run_etl():
    # ==========================================
    # 1. EXTRACT
    # ==========================================
    print("Extracting data...")
    prices = pd.read_excel(
        NRAUS_FILE, sheet_name="AUS Food Price database", skiprows=10, header=None,
        usecols="A:G", dtype=str,
        names=["category", "category_desc", "brand", "product_name", "size_g", "ausnut_2011_code", "cost_aud"],
    )
    match = pd.read_excel(MATCH_FILE, sheet_name="TAB A - Matching file", header=3, dtype=str)
    nutrients = pd.read_excel(NUTRIENT_FILE, sheet_name="Food nutrient profiles", header=2)
    details = pd.read_excel(
        DETAILS_FILE, sheet_name="Food details", skiprows=4, header=None,
        usecols="A,C,E,F,O", dtype=str,
        names=["survey_id", "food_key", "ausnut_name", "food_description", "food_group"],
    )
    unmatched_2011 = pd.read_excel(MATCH_FILE, sheet_name="TAB B - Unmatched 2011-13 foods", header=3, dtype=str)
    details["ausnut_name"] = details["ausnut_name"].str.strip()
    # ==========================================
    # 2. TRANSFORM
    # ==========================================
    print("Transforming data...")

    # NRAUS: category names only appear on their own row, so push them down to the product rows
    prices["category"] = prices["category"].ffill()
    prices["ausnut_2011_code"] = prices["ausnut_2011_code"].str.strip()
    prices = prices[prices["ausnut_2011_code"].str.fullmatch(r"\d{8}", na=False)].copy()
    for col in ["category", "brand", "product_name"]:
        prices[col] = prices[col].fillna("").str.strip()
    prices["size_g"] = pd.to_numeric(prices["size_g"])
    prices["cost_aud"] = pd.to_numeric(prices["cost_aud"])
    print(f"  price rows: {len(prices)}")

    # Each product was priced at several stores; average them into one row
    products = prices.groupby(
        ["category", "brand", "product_name", "size_g", "ausnut_2011_code"], as_index=False
    ).agg(cost_aud=("cost_aud", "mean"), price_samples=("cost_aud", "size"))
    products["cost_aud"] = products["cost_aud"].round(2)
    products["price_per_100g"] = (products["cost_aud"] / products["size_g"] * 100).round(3)
    print(f"  unique products: {len(products)}")

    # Exact join: 2011-13 code -> 2023 public food key
    match = match.rename(columns={"Public food key": "food_key", "Survey ID.1": "ausnut_2011_code"})
    match = match[["food_key", "ausnut_2011_code"]].dropna()
    match["ausnut_2011_code"] = match["ausnut_2011_code"].str.strip()
    products = products.merge(match, on="ausnut_2011_code", how="left")
    products["match_method"] = products["food_key"].notna().map({True: "exact", False: None})
    products["match_score"] = products["food_key"].notna().astype(float)
    print(f"  exact matches: {products['food_key'].notna().sum()}")

    # Fuzzy fallback for codes the matching file doesn't cover
    nutrients = nutrients.rename(columns={
        "Public food key": "food_key",
        "Energy with dietary fibre (kJ)": "energy_kj",
        "Protein (g)": "protein_g",
        "Total fat (g)": "fat_g",
        "Dietary fibre (g)": "fibre_g",
        "Total sugars (g)": "sugars_g",
    })
    carbs_col = next(c for c in nutrients.columns if c.startswith("Available carbohydrate, with sugar alcohols"))
    nutrients = nutrients.rename(columns={carbs_col: "carbs_g"})[["food_key"] + MACRO_COLS]

    names_2011 = dict(zip(unmatched_2011["Survey ID"].str.strip(), unmatched_2011["Food name"]))
    candidates = details[details["food_key"].isin(nutrients["food_key"])]
    key_by_name = dict(zip(candidates["ausnut_name"], candidates["food_key"]))
    name_by_key = dict(zip(candidates["food_key"], candidates["ausnut_name"]))

    for idx in products.index[products["food_key"].isna()]:
        row = products.loc[idx]
        code = row["ausnut_2011_code"]
        if code in MANUAL_MATCHES:
            key, method, score = key_by_name[MANUAL_MATCHES[code]], "manual", 1.0
        else:
            key, score = best_fuzzy_match(code, names_2011.get(code, row["product_name"]), candidates)
            method = "fuzzy"
        if key:
            products.loc[idx, ["food_key", "match_method", "match_score"]] = [key, method, score]
            print(f"  {method} {score:.2f}: {row['product_name']!r} -> {name_by_key[key]!r}")
        else:
            print(f"  dropped: {row['product_name']!r} ({code})")

    # Attach nutrients (per 100 g) and descriptions
    products = products.merge(nutrients, on="food_key", how="left")
    products = products.merge(
        details[["food_key", "ausnut_name", "food_description", "food_group"]], on="food_key", how="left"
    )
    products[MACRO_COLS] = products[MACRO_COLS].apply(pd.to_numeric, errors="coerce")
    products["kcal"] = (products["energy_kj"] / 4.184).round(1)

    # Words only: numbers belong in filters, not in the embedding text
    products["search_text"] = (
        products["product_name"] + ". " + products["category"] + ". " + products["food_description"].fillna("")
    )
    products["_id"] = (
        products["brand"] + "|" + products["product_name"] + "|" + products["size_g"].astype(int).astype(str)
    )
    products = products.drop_duplicates(subset="_id")
    products["price_source"] = "NRAUS Dec 2020 (Coles/Woolworths NSW)"
    products["nutrient_source"] = "AUSNUT 2023"
    print(f"  documents ready: {len(products)}")

    # ==========================================
    # 3. LOAD (Upsert)
    # ==========================================
    print("Loading into local MongoDB...")
    client = MongoClient("mongodb://localhost:27017/")
    collection = client["nutrition_db"]["products"]

    # MongoDB can't store NaN meaningfully; missing nutrients become null, never 0
    records = products.astype(object).where(products.notna(), None).to_dict(orient="records")
    operations = [ReplaceOne({"_id": r["_id"]}, r, upsert=True) for r in records]
    if operations:
        result = collection.bulk_write(operations)
        collection.delete_many({"_id": {"$nin": [r["_id"] for r in records]}})
        print(f"Load complete. Matched: {result.matched_count}, Modified: {result.modified_count}, Upserted: {result.upserted_count}")
    collection.create_index("protein_g")
    collection.create_index("price_per_100g")
    collection.create_index("category")

    # ==========================================
    # 4. VERIFY
    # ==========================================
    print("\nVerifying database with queries...")
    query = {"protein_g": {"$gte": 20}, "price_per_100g": {"$lte": 5}}
    projection = {"_id": 0, "brand": 1, "product_name": 1, "protein_g": 1, "price_per_100g": 1}
    print("High-protein, budget-friendly items found:")
    for item in collection.find(query, projection).sort("price_per_100g", 1).limit(10):
        print(f"- {item['brand']} {item['product_name']}: {item['protein_g']}g protein, ${item['price_per_100g']}/100g")


if __name__ == "__main__":
    run_etl()