import type { Meal, TargetFormState } from "../types";

interface Props {
  meal: Meal;
  targets: TargetFormState;
}

function clampPct(n: number) {
  return Math.max(0, Math.min(100, n));
}

export default function MacroBars({ meal, targets }: Props) {
  const { totals } = meal;
  // Prefer shopping-list pack prices (what packs cost at the till)
  const packCost = meal.shopping_list.reduce(
    (sum, item) => sum + item.packs * item.pack_price_aud,
    0,
  );
  const costAud = packCost > 0 ? packCost : totals.cost_aud;
  const proteinPct = clampPct((totals.protein_g / targets.min_protein_g) * 100);
  const kcalPct = clampPct((totals.kcal / targets.max_kcal) * 100);
  const costPct = clampPct((costAud / targets.max_budget_aud) * 100);
  const proteinOk = totals.protein_g + 0.05 >= targets.min_protein_g;
  const kcalOk =
    totals.kcal <= targets.max_kcal + 0.5 &&
    (targets.min_kcal == null || totals.kcal + 0.5 >= targets.min_kcal);
  const costOk = costAud <= targets.max_budget_aud + 0.01;

  return (
    <section className="panel result-panel glass">
      <header className="panel-header">
        <p className="eyebrow">Totals</p>
        <h2>Macros vs targets</h2>
      </header>

      <div className="bars">
        <div className={`bar-row ${proteinOk ? "" : "warn"}`}>
          <div className="bar-label">
            <span>Protein</span>
            <span>
              {totals.protein_g.toFixed(1)} / {targets.min_protein_g} g
            </span>
          </div>
          <div className="bar-track">
            <div className="bar-fill" style={{ width: `${proteinPct}%` }} />
          </div>
        </div>

        <div className={`bar-row ${kcalOk ? "" : "warn"}`}>
          <div className="bar-label">
            <span>Calories</span>
            <span>
              {totals.kcal.toFixed(0)}
              {targets.min_kcal != null ? ` (${targets.min_kcal}–${targets.max_kcal})` : ` / ${targets.max_kcal}`}{" "}
              kcal
            </span>
          </div>
          <div className="bar-track">
            <div className="bar-fill" style={{ width: `${kcalPct}%` }} />
          </div>
        </div>

        <div className={`bar-row ${costOk ? "" : "warn"}`}>
          <div className="bar-label">
            <span>Pack cost</span>
            <span>
              ${costAud.toFixed(2)} / ${targets.max_budget_aud.toFixed(2)}
            </span>
          </div>
          <div className="bar-track">
            <div className="bar-fill" style={{ width: `${costPct}%` }} />
          </div>
        </div>
      </div>

      {meal.unmet_targets.length > 0 && (
        <ul className="unmet">
          {meal.unmet_targets.map((msg) => (
            <li key={msg}>{msg}</li>
          ))}
        </ul>
      )}
    </section>
  );
}
