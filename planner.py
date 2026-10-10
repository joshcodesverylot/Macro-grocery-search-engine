"""
Search -> Gemini draft -> validate ids -> optimise grams -> Meal.

Plain Python; FastAPI comes later in api.py and only wraps generate_meal.
"""
import math

from pydantic import ValidationError

from llm import draft_meal
from models import Meal, MealItem, MealRequest, ShoppingItem, Totals
from optimizer import optimise_grams
from retrieval import DAIRY_CATEGORIES, search

MAX_ATTEMPTS = 3  # first try + up to 2 retries
SYSTEM = (
    "You are an Australian meal planner. Pick 3 to 6 products from the candidate list only. "
    "Use each product_id exactly as given. suggested_grams is a rough portion in grams; "
    "an optimiser will adjust it. Never invent products."
)


def build_query(request):
    parts = [request.meal_type]
    if request.preference:
        parts.append(request.preference)
    if request.mode == "quick":
        parts.append("ready to eat no cooking")
    return " ".join(parts)


def fetch_candidates(request):
    return search(
        query=build_query(request),
        exclude_categories=DAIRY_CATEGORIES if request.dairy_free else None,
        ready_to_eat=True if request.mode == "quick" else None,
        exclude_ids=request.exclude_ids or None,
        max_per_category=3,
        k=25,
    )


def format_candidates(candidates):
    lines = ["id | brand | name | category | kcal/100g | protein g/100g | $/100g"]
    for c in candidates:
        lines.append(
            f"{c['id']} | {c['brand']} | {c['product_name']} | {c['category']} | "
            f"{c['kcal']} | {c['protein_g']} | {c['price_per_100g']}"
        )
    return "\n".join(lines)


def build_prompt(request, candidates, feedback=None):
    mode_rule = (
        "Mode: quick. Only ready-to-eat products; steps must need no cooking or stove."
        if request.mode == "quick"
        else "Mode: cook. Steps may include cooking."
    )
    kcal_line = f"at most {request.max_kcal:.0f} kcal"
    if request.min_kcal is not None:
        kcal_line = f"between {request.min_kcal:.0f} and {request.max_kcal:.0f} kcal"
    prompt = (
        f"Create one {request.meal_type}.\n"
        f"{mode_rule}\n"
        f"Targets: at least {request.min_protein_g:.0f} g protein, {kcal_line}, "
        f"budget at most ${request.max_budget_aud:.2f}.\n"
        "Rules: use only product_id values from the list below; pick 3 to 6 items; "
        "prefer a coherent single meal over random high-protein foods.\n\n"
        f"Candidates:\n{format_candidates(candidates)}"
    )
    if feedback:
        prompt += f"\n\nPrevious attempt failed:\n{feedback}\nFix that and try again."
    return prompt


def unknown_ids(draft, allowed_ids):
    return [item.product_id for item in draft.items if item.product_id not in allowed_ids]


def portion(product, grams):
    scale = grams / 100
    return {
        "kcal": round(product["kcal"] * scale, 1),
        "protein_g": round(product["protein_g"] * scale, 1),
        "fat_g": round((product.get("fat_g") or 0) * scale, 1),
        "carbs_g": round((product.get("carbs_g") or 0) * scale, 1),
        "cost_aud": round(product["price_per_100g"] * scale, 2),
    }


def build_meal(request, draft, products, grams, unmet_targets=None):
    items = []
    shopping = []
    totals = {"kcal": 0.0, "protein_g": 0.0, "fat_g": 0.0, "carbs_g": 0.0, "cost_aud": 0.0}
    for product, g in zip(products, grams):
        macros = portion(product, g)
        items.append(MealItem(
            product_id=product["id"],
            brand=product["brand"],
            product_name=product["product_name"],
            category=product["category"],
            grams=g,
            **macros,
        ))
        for key in totals:
            totals[key] += macros[key]
        size = float(product["size_g"])
        packs = max(1, math.ceil(g / size)) if size > 0 else 1
        shopping.append(ShoppingItem(
            product_id=product["id"],
            brand=product["brand"],
            product_name=product["product_name"],
            size_g=size,
            pack_price_aud=float(product["cost_aud"]),
            packs=packs,
        ))
    return Meal(
        title=draft.title,
        meal_type=request.meal_type,
        mode=request.mode,
        items=items,
        steps=draft.steps,
        totals=Totals(
            kcal=round(totals["kcal"], 1),
            protein_g=round(totals["protein_g"], 1),
            fat_g=round(totals["fat_g"], 1),
            carbs_g=round(totals["carbs_g"], 1),
            cost_aud=round(totals["cost_aud"], 2),
        ),
        unmet_targets=unmet_targets or [],
        shopping_list=shopping,
    )


def generate_meal(request: MealRequest) -> Meal:
    candidates = fetch_candidates(request)
    if not candidates:
        raise ValueError("No products matched the filters. Loosen the targets or clear exclude_ids.")

    by_id = {c["id"]: c for c in candidates}
    feedback = None
    last_meal = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            draft = draft_meal(build_prompt(request, candidates, feedback), system_instruction=SYSTEM)
        except ValidationError as e:
            feedback = f"Schema error: {e.errors()[0]['msg']}"
            print(f"  attempt {attempt}: {feedback}")
            continue

        bad = unknown_ids(draft, by_id)
        if bad:
            feedback = f"Unknown product_id values (not in the candidate list): {bad}"
            print(f"  attempt {attempt}: {feedback}")
            continue

        products = [by_id[item.product_id] for item in draft.items]
        suggested = [item.suggested_grams for item in draft.items]
        result = optimise_grams(
            products,
            suggested,
            min_protein_g=request.min_protein_g,
            max_kcal=request.max_kcal,
            max_budget_aud=request.max_budget_aud,
            min_kcal=request.min_kcal,
        )

        if result.grams is None:
            # Soft fallback: use the LLM's suggested grams so the UI still has something to show
            last_meal = build_meal(request, draft, products, suggested, unmet_targets=result.unmet_targets)
            feedback = "Optimiser could not hit targets:\n- " + "\n- ".join(result.unmet_targets)
            print(f"  attempt {attempt}: infeasible")
            continue

        meal = build_meal(request, draft, products, result.grams)
        print(f"  attempt {attempt}: ok")
        return meal

    if last_meal is not None:
        return last_meal
    raise RuntimeError(f"Failed to generate a meal after {MAX_ATTEMPTS} attempts. Last feedback: {feedback}")


def show(meal):
    print(f"\n=== {meal.title} ({meal.meal_type}, {meal.mode}) ===")
    for item in meal.items:
        print(f"  {item.grams:>5.0f} g  {item.brand} {item.product_name}  "
              f"{item.protein_g}g protein  {item.kcal} kcal  ${item.cost_aud}")
    t = meal.totals
    print(f"  TOTAL: {t.protein_g}g protein, {t.kcal} kcal, ${t.cost_aud}")
    if meal.unmet_targets:
        print("  unmet:", meal.unmet_targets)
    print("  steps:")
    for i, step in enumerate(meal.steps, 1):
        print(f"    {i}. {step}")
    print("  shopping:")
    for s in meal.shopping_list:
        print(f"    {s.packs} x {s.brand} {s.product_name} ({s.size_g:g} g) @ ${s.pack_price_aud}")


if __name__ == "__main__":
    req = MealRequest(
        meal_type="dinner",
        mode="cook",
        min_protein_g=40,
        max_kcal=700,
        max_budget_aud=10,
        min_kcal=350,
    )
    print("Generating dinner...")
    show(generate_meal(req))
