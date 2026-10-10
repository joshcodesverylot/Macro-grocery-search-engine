from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import linprog

MIN_SCALE, MAX_SCALE = 0.5, 1.5


@dataclass
class OptimiseResult:
    grams: list[float] | None          # None when no grams satisfy every target
    unmet_targets: list[str] = field(default_factory=list)


def per_gram(products, key):
    return np.array([float(p[key] or 0) for p in products]) / 100


def explain_infeasible(protein, kcal, price, low, high, min_protein_g, max_kcal, max_budget_aud, min_kcal):
    # Check each target alone at its most favourable extreme; these messages become LLM retry feedback
    reasons = []
    best_protein = protein @ high
    if best_protein < min_protein_g:
        reasons.append(f"protein: at most {best_protein:.0f} g reachable, target is {min_protein_g:.0f} g "
                       f"(choose higher-protein products or larger portions)")
    lowest_kcal = kcal @ low
    if lowest_kcal > max_kcal:
        reasons.append(f"kcal: at least {lowest_kcal:.0f} kcal, limit is {max_kcal:.0f} "
                       f"(choose lower-calorie products or smaller portions)")
    lowest_cost = price @ low
    if lowest_cost > max_budget_aud:
        reasons.append(f"budget: at least ${lowest_cost:.2f}, budget is ${max_budget_aud:.2f} "
                       f"(choose cheaper products)")
    if min_kcal is not None and kcal @ high < min_kcal:
        reasons.append(f"kcal: at most {kcal @ high:.0f} kcal reachable, minimum is {min_kcal:.0f} "
                       f"(choose more filling products or larger portions)")
    if not reasons:
        reasons.append("targets conflict: each is reachable alone but not all together "
                       "(e.g. enough protein pushes kcal or cost over the limit)")
    return reasons


def optimise_grams(products, suggested_grams, min_protein_g, max_kcal, max_budget_aud, min_kcal=None):
    """Cheapest grams for each product, within 50-150% of the suggestion, that hit every target.

    products: dicts with price_per_100g, kcal and protein_g (e.g. retrieval.search results)
    """
    suggested = np.array(suggested_grams, dtype=float)
    low, high = suggested * MIN_SCALE, suggested * MAX_SCALE
    price, protein, kcal = per_gram(products, "price_per_100g"), per_gram(products, "protein_g"), per_gram(products, "kcal")

    # linprog only accepts "<=", so minimums are negated: protein >= x becomes -protein <= -x
    A_ub = [-protein, kcal, price]
    b_ub = [-min_protein_g, max_kcal, max_budget_aud]
    if min_kcal is not None:
        A_ub.append(-kcal)
        b_ub.append(-min_kcal)

    result = linprog(c=price, A_ub=A_ub, b_ub=b_ub, bounds=list(zip(low, high)), method="highs")
    if not result.success:
        return OptimiseResult(None, explain_infeasible(protein, kcal, price, low, high,
                                                       min_protein_g, max_kcal, max_budget_aud, min_kcal))
    return OptimiseResult(np.round(result.x).tolist())


if __name__ == "__main__":
    products = [
        {"product_name": "Extra Lean Beef Mince", "price_per_100g": 1.8, "kcal": 129.3, "protein_g": 22.9},
        {"product_name": "Brushed Potatoes", "price_per_100g": 0.275, "kcal": 57.8, "protein_g": 2.3},
        {"product_name": "Broccoli", "price_per_100g": 0.25, "kcal": 32.0, "protein_g": 4.0},
        {"product_name": "Carrots", "price_per_100g": 0.133, "kcal": 34.7, "protein_g": 0.6},
    ]
    suggested = [150, 200, 100, 80]
    for targets in [dict(min_protein_g=50, max_kcal=600, max_budget_aud=6),
                    dict(min_protein_g=50, max_kcal=600, max_budget_aud=6, min_kcal=450),
                    dict(min_protein_g=80, max_kcal=600, max_budget_aud=6),
                    dict(min_protein_g=50, max_kcal=600, max_budget_aud=2)]:
        r = optimise_grams(products, suggested, **targets)
        print(targets, "->", r.grams if r.grams else r.unmet_targets)
