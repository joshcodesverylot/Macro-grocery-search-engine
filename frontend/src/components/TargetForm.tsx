import type { MealMode, MealType, TargetFormState } from "../types";

interface Props {
  value: TargetFormState;
  onChange: (next: TargetFormState) => void;
  onGenerate: () => void;
  loading: boolean;
  invalidMinKcal: boolean;
}

export default function TargetForm({ value, onChange, onGenerate, loading, invalidMinKcal }: Props) {
  const set = <K extends keyof TargetFormState>(key: K, next: TargetFormState[K]) =>
    onChange({ ...value, [key]: next });

  return (
    <section className="panel form-panel glass">
      <header className="panel-header">
        <p className="eyebrow">Targets</p>
        <h2>Build one meal</h2>
      </header>

      <div className="field-grid">
        <label className="field glass-control">
          <span>Meal type</span>
          <select
            value={value.meal_type}
            onChange={(e) => set("meal_type", e.target.value as MealType)}
          >
            <option value="breakfast">Breakfast</option>
            <option value="lunch">Lunch</option>
            <option value="dinner">Dinner</option>
            <option value="snack">Snack</option>
          </select>
        </label>

        <label className="field glass-control">
          <span>Mode</span>
          <div className="segmented">
            {(["quick", "cook"] as MealMode[]).map((mode) => (
              <button
                key={mode}
                type="button"
                className={value.mode === mode ? "active" : ""}
                onClick={() => set("mode", mode)}
              >
                {mode === "quick" ? "Quick" : "Cook"}
              </button>
            ))}
          </div>
        </label>

        <label className="field glass-control slider-field">
          <span>
            Min protein <strong>{value.min_protein_g} g</strong>
          </span>
          <input
            type="range"
            min={10}
            max={80}
            step={1}
            value={value.min_protein_g}
            onChange={(e) => set("min_protein_g", Number(e.target.value))}
          />
        </label>

        <label className="field glass-control slider-field">
          <span>
            Max calories <strong>{value.max_kcal} kcal</strong>
          </span>
          <input
            type="range"
            min={200}
            max={1200}
            step={10}
            value={value.max_kcal}
            onChange={(e) => set("max_kcal", Number(e.target.value))}
          />
        </label>

        <label className="field glass-control slider-field">
          <span>
            Min calories{" "}
            <strong>{value.min_kcal == null ? "off" : `${value.min_kcal} kcal`}</strong>
          </span>
          <input
            type="range"
            min={0}
            max={800}
            step={10}
            value={value.min_kcal ?? 0}
            onChange={(e) => {
              const n = Number(e.target.value);
              set("min_kcal", n === 0 ? null : n);
            }}
          />
        </label>

        <label className="field glass-control slider-field">
          <span>
            Budget <strong>${value.max_budget_aud.toFixed(0)}</strong>
          </span>
          <input
            type="range"
            min={2}
            max={45}
            step={1}
            value={value.max_budget_aud}
            onChange={(e) => set("max_budget_aud", Number(e.target.value))}
          />
        </label>

        <label className="field glass-control toggle-field">
          <span>Dairy free</span>
          <input
            type="checkbox"
            checked={value.dairy_free}
            onChange={(e) => set("dairy_free", e.target.checked)}
          />
        </label>

        <label className="field glass-control preference-field">
          <span>Preference</span>
          <input
            type="text"
            placeholder="e.g. something sweet, high fibre"
            value={value.preference}
            onChange={(e) => set("preference", e.target.value)}
          />
        </label>
      </div>

      {invalidMinKcal && (
        <p className="inline-error">Min calories must be less than max calories.</p>
      )}

      <button
        type="button"
        className="generate-btn"
        disabled={loading || invalidMinKcal}
        onClick={onGenerate}
      >
        {loading ? "Generating…" : "Generate meal"}
      </button>
    </section>
  );
}
