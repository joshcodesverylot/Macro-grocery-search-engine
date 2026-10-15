import type { Meal } from "../types";

interface Props {
  meal: Meal;
  loading: boolean;
  onSwap: (productId: string) => void;
  onSomethingElse: () => void;
}

export default function MealCard({ meal, loading, onSwap, onSomethingElse }: Props) {
  return (
    <section className="panel result-panel glass">
      <header className="panel-header meal-header">
        <div>
          <p className="eyebrow">
            {meal.meal_type} · {meal.mode}
          </p>
          <h2>{meal.title}</h2>
        </div>
        <button type="button" className="ghost-btn" disabled={loading} onClick={onSomethingElse}>
          Something else
        </button>
      </header>

      <ul className="ingredient-list">
        {meal.items.map((item) => (
          <li key={item.product_id} className="ingredient-row glass-control">
            <div className="ingredient-main">
              <strong>
                {item.brand} {item.product_name}
              </strong>
              <span className="muted">
                {item.grams.toFixed(0)} g · {item.protein_g.toFixed(1)} g protein · {item.kcal.toFixed(0)}{" "}
                kcal · ${item.cost_aud.toFixed(2)}
              </span>
              <span className="muted thin">
                fat {item.fat_g.toFixed(1)} g · carbs {item.carbs_g.toFixed(1)} g · {item.category}
              </span>
            </div>
            <button
              type="button"
              className="ghost-btn compact"
              disabled={loading}
              onClick={() => onSwap(item.product_id)}
            >
              Swap
            </button>
          </li>
        ))}
      </ul>

      <div className="steps">
        <h3>Steps</h3>
        <ol>
          {meal.steps.map((step, i) => (
            <li key={`${i}-${step.slice(0, 24)}`}>{step}</li>
          ))}
        </ol>
      </div>
    </section>
  );
}
