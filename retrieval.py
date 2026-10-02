import numpy as np
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
FETCH_FIELDS = {
    "_id": 1, "brand": 1, "product_name": 1, "size_g": 1, "category": 1, "search_text": 1,
    "cost_aud": 1, "price_per_100g": 1, "kcal": 1, "protein_g": 1, "fat_g": 1, "carbs_g": 1,
    "fibre_g": 1, "ready_to_eat": 1, "embedding": 1,
}
DAIRY_CATEGORIES = [
    "Dairy milk, full fat", "Dairy milk, reduced fat or skim", "Flavoured milk", "Cream",
    "Cheese", "Ultra-processed cheese", "Yoghurt, full fat", "Yoghurt, reduced fat",
    "Liquid breakfast, fortified beverages (like Milo)",
]

# Loaded once when the file is imported; loading takes seconds, encoding a query takes milliseconds
model = SentenceTransformer(MODEL_NAME)
collection = MongoClient("mongodb://localhost:27017/")["nutrition_db"]["products"]


def build_filter(min_protein_g=None, max_price_per_100g=None, max_kcal=None, exclude_categories=None,
                 ready_to_eat=None, exclude_ids=None):
    mongo_filter = {"embedding": {"$exists": True}}
    if min_protein_g is not None:
        mongo_filter["protein_g"] = {"$gte": min_protein_g}
    if max_price_per_100g is not None:
        mongo_filter["price_per_100g"] = {"$lte": max_price_per_100g}
    if max_kcal is not None:
        mongo_filter["kcal"] = {"$lte": max_kcal}
    if exclude_categories is not None:
        mongo_filter["category"] = {"$nin": exclude_categories}
    # "is not None" so that False (cook mode) still applies
    if ready_to_eat is not None:
        mongo_filter["ready_to_eat"] = ready_to_eat
    if exclude_ids:
        mongo_filter["_id"] = {"$nin": exclude_ids}
    return mongo_filter



def keep_cheapest(docs):
    cheapest = {}
    for doc in docs:
        text = doc["search_text"]
        if text not in cheapest or doc["price_per_100g"] < cheapest[text]["price_per_100g"]:
            cheapest[text] = doc
    return list(cheapest.values())


def to_result(doc, score):
    # TODO 2: return a plain dict describing one product, WITHOUT "embedding" or "search_text".
    # Hints:
    #   - include "id" (from doc["_id"]), brand, product_name, size_g, category,
    #     cost_aud, price_per_100g, kcal, protein_g, fat_g, carbs_g, and "score"
    #   - wrap the score in float(...): numpy numbers can't be turned into JSON later by FastAPI
    #   - round the score to 3 decimal places so it prints neatly
    return {
        "id": doc["_id"],
        "brand": doc["brand"],
        "product_name": doc["product_name"],
        "size_g": doc["size_g"],
        "category": doc["category"],
        "cost_aud": doc["cost_aud"],
        "price_per_100g": doc["price_per_100g"],
        "kcal": doc["kcal"],
        "protein_g": doc["protein_g"],
        "fat_g": doc["fat_g"],
        "carbs_g": doc["carbs_g"],
        "fibre_g": doc["fibre_g"],
        "ready_to_eat": doc["ready_to_eat"],
        "score": round(float(score), 3),
    }


def search(query, min_protein_g=None, max_price_per_100g=None, max_kcal=None, exclude_categories=None,
           ready_to_eat=None, exclude_ids=None, max_per_category=None, k=20):
    mongo_filter = build_filter(min_protein_g, max_price_per_100g, max_kcal, exclude_categories,
                                ready_to_eat, exclude_ids)
    if exclude_ids:
        # Also exclude other sizes/brands of the same food, otherwise "something else" brings it straight back
        excluded_texts = collection.distinct("search_text", {"_id": {"$in": exclude_ids}})
        mongo_filter["search_text"] = {"$nin": excluded_texts}
    docs = list(collection.find(mongo_filter, FETCH_FIELDS))
    docs = keep_cheapest(docs)
    if not docs:
        return []
    matrix = np.array([doc["embedding"] for doc in docs])
    query_vector = model.encode(query, normalize_embeddings=True)
    scores = matrix @ query_vector
    # A loop rather than [:k]: items skipped by the category cap are replaced by the next best
    results, per_category = [], {}
    for i in np.argsort(scores)[::-1]:
        category = docs[i]["category"]
        if max_per_category is not None and per_category.get(category, 0) >= max_per_category:
            continue
        results.append(to_result(docs[i], scores[i]))
        per_category[category] = per_category.get(category, 0) + 1
        if len(results) == k:
            break
    return results
    

def show(title, results):
    print(f"\n=== {title} ({len(results)} results) ===")
    for r in results:
        name = f"{r['brand']} {r['product_name']}"
        print(f"  {r['score']:.3f}  {name[:45]:<45} {r['protein_g']}g protein  "
              f"${r['price_per_100g']}/100g  {r['kcal']} kcal  [{r['category']}]")


if __name__ == "__main__":
    show("breakfast, protein >= 10g, <= $1.50/100g",
         search("cheap high protein breakfast", min_protein_g=10, max_price_per_100g=1.5, k=5))
    show("dinner, protein >= 15g",
         search("hearty dinner", min_protein_g=15, k=5))
    show("breakfast without dairy (category filter)",
         search("breakfast", exclude_categories=DAIRY_CATEGORIES, k=5))
    show("impossible filter", search("anything", min_protein_g=500))

    quick = search("breakfast", ready_to_eat=True, k=5)
    show("quick breakfast (all should be ready to eat)", quick)
    show("cook-mode dinner (all should need cooking)", search("dinner", ready_to_eat=False, k=5))
    swapped = search("breakfast", ready_to_eat=True, exclude_ids=[r["id"] for r in quick], k=5)
    show("something else (no overlap with quick breakfast)", swapped)
    show("breakfast, max 1 per category", search("breakfast", max_per_category=1, k=5))
