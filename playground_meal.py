"""
Playground: the two pieces that sit between retrieval and the UI.

  retrieval.search() -> [LLM writes a MealDraft] -> Part 1: validate it -> Part 2: optimise grams -> Meal

No LLM or MongoDB here: the "LLM output" is hand-written JSON and the products are real rows
copied from MongoDB, so this runs instantly and you can poke at it freely.
"""
import numpy as np
from pydantic import BaseModel, Field, ValidationError
from scipy.optimize import linprog

# Real products (per 100 g), copied from nutrition_db.products. In the app these come from search().
PRODUCTS = {
    "Coles|5 Star Extra Lean Beef Mince|500": {"name": "Extra Lean Beef Mince", "price_per_100g": 1.8,   "kcal": 129.3, "protein_g": 22.9},
    "Woolworths|Brushed Potatoes|2000":       {"name": "Brushed Potatoes",      "price_per_100g": 0.275, "kcal": 57.8,  "protein_g": 2.3},
    "Coles|Broccoli|1000":                    {"name": "Broccoli",              "price_per_100g": 0.25,  "kcal": 32.0,  "protein_g": 4.0},
    "Coles|I'm Perfect Carrots Prepacked|1500": {"name": "Carrots",             "price_per_100g": 0.133, "kcal": 34.7,  "protein_g": 0.6},
}


# ==========================================
# PART 1: PYDANTIC - is the LLM's answer even usable?
# ==========================================
# You already know BaseModel from test_pydantic.py. New here:
#   - Field(gt=0, le=1000)      rejects 0 g or 5000 g of beef before any maths runs
#   - Field(min_length=3, ...)  on a list: a "meal" of one item is rejected
#   - Pydantic can't know which ids are real (that depends on what search() returned),
#     so that check is a plain function, done right after validation.

class DraftItem(BaseModel):
    product_id: str
    suggested_grams: float = Field(gt=0, le=1000)


class MealDraft(BaseModel):
    title: str
    items: list[DraftItem] = Field(min_length=3, max_length=6)
    steps: list[str]


def find_unknown_ids(draft, allowed_ids):
    # An empty list means every ingredient came from the retrieved products (no hallucinations)
    return [item.product_id for item in draft.items if item.product_id not in allowed_ids]


GOOD_JSON = """{
  "title": "Beef mince with mash and greens",
  "items": [
    {"product_id": "Coles|5 Star Extra Lean Beef Mince|500", "suggested_grams": 150},
    {"product_id": "Woolworths|Brushed Potatoes|2000", "suggested_grams": 200},
    {"product_id": "Coles|Broccoli|1000", "suggested_grams": 100},
    {"product_id": "Coles|I'm Perfect Carrots Prepacked|1500", "suggested_grams": 80}
  ],
  "steps": ["Brown the mince", "Boil and mash the potatoes", "Steam the broccoli and carrots"]
}"""

BAD_GRAMS_JSON = GOOD_JSON.replace('"suggested_grams": 150', '"suggested_grams": 0')
TOO_FEW_JSON = """{"title": "Just beef", "steps": ["Cook it"],
  "items": [{"product_id": "Coles|5 Star Extra Lean Beef Mince|500", "suggested_grams": 300}]}"""
MADE_UP_ID_JSON = GOOD_JSON.replace("Coles|Broccoli|1000", "Coles|Wagyu Steak|300")


def part1():
    print("=== PART 1: validation ===")
    for label, raw in [("good", GOOD_JSON), ("0 g of beef", BAD_GRAMS_JSON),
                       ("only 1 item", TOO_FEW_JSON), ("made-up id", MADE_UP_ID_JSON)]:
        try:
            draft = MealDraft.model_validate_json(raw)
        except ValidationError as e:
            # e.errors() is a list of dicts; "loc" says WHERE, "msg" says WHAT. This text is what
            # planner.py will send back to the LLM on a retry.
            first = e.errors()[0]
            print(f"  {label:<12} REJECTED by Pydantic at {first['loc']}: {first['msg']}")
            continue
        unknown = find_unknown_ids(draft, PRODUCTS.keys())
        if unknown:
            print(f"  {label:<12} REJECTED: not in retrieved products: {unknown}")
        else:
            print(f"  {label:<12} OK: '{draft.title}' with {len(draft.items)} items")


# ==========================================
# PART 2: OPTIMISER - pick exact grams that hit the targets
# ==========================================
# LLMs are bad at arithmetic, so the LLM only picks WHAT to eat and roughly how much.
# linprog then picks exact grams g1..gn. It solves:
#
#   minimise   c @ g                     (c = cost per gram -> cheapest meal)
#   subject to A_ub @ g <= b_ub          (every constraint must be written as "<=")
#              low_i <= g_i <= high_i    (bounds: 50%..150% of the LLM's suggestion, keeps the recipe recognisable)
#
# Per-gram values are per_100g / 100, so e.g. protein of the meal = sum(protein_per_gram_i * g_i).
#
# The "<=" trick for a minimum: "protein >= 50" is the same as "-protein <= -50" (multiply both sides by -1).

def optimise_grams(draft, min_protein_g, max_kcal, max_budget_aud):
    rows = [PRODUCTS[item.product_id] for item in draft.items]
    suggested = np.array([item.suggested_grams for item in draft.items])

    price = np.array([r["price_per_100g"] for r in rows]) / 100   # $ per gram
    protein = np.array([r["protein_g"] for r in rows]) / 100      # g protein per gram
    kcal = np.array([r["kcal"] for r in rows]) / 100              # kcal per gram

    # One row per constraint, each already in "<=" form
    A_ub = [-protein, kcal, price]
    b_ub = [-min_protein_g, max_kcal, max_budget_aud]
    bounds = [(0.5 * s, 1.5 * s) for s in suggested]

    result = linprog(c=price, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")

    # Not successful means no grams within the bounds can satisfy every target
    if not result.success:
        return None
    return np.round(result.x)


def print_meal(draft, grams):
    total = {"protein_g": 0.0, "kcal": 0.0, "cost": 0.0}
    for item, g in zip(draft.items, grams):
        p = PRODUCTS[item.product_id]
        total["protein_g"] += p["protein_g"] * g / 100
        total["kcal"] += p["kcal"] * g / 100
        total["cost"] += p["price_per_100g"] * g / 100
        print(f"    {p['name']:<24} suggested {item.suggested_grams:>5.0f} g -> {g:>5.0f} g")
    print(f"    TOTAL: {total['protein_g']:.1f} g protein, {total['kcal']:.0f} kcal, ${total['cost']:.2f}")


def part2():
    print("\n=== PART 2: optimiser ===")
    draft = MealDraft.model_validate_json(GOOD_JSON)
    print("  As the LLM suggested (before optimising):")
    print_meal(draft, [item.suggested_grams for item in draft.items])

    for targets in [dict(min_protein_g=50, max_kcal=600, max_budget_aud=6),
                    dict(min_protein_g=80, max_kcal=600, max_budget_aud=6)]:
        print(f"\n  Targets: {targets}")
        grams = optimise_grams(draft, **targets)
        if grams is None:
            print("    INFEASIBLE: no grams within 50-150% can hit these targets")
        else:
            print_meal(draft, grams)


if __name__ == "__main__":
    part1()
    part2()
