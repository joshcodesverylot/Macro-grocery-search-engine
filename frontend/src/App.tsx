import { useEffect, useMemo, useState } from "react";
import { checkHealth, generateMeal } from "./api";
import FoodParticleField from "./components/FoodParticleField";
import MealCard from "./components/MealCard";
import MacroBars from "./components/MacroBars";
import ShoppingList from "./components/ShoppingList";
import TargetForm from "./components/TargetForm";
import type { Meal, MealRequest, TargetFormState } from "./types";
import "./App.css";

const STORAGE_KEY = "mealTargets";

const DEFAULTS: TargetFormState = {
  meal_type: "dinner",
  mode: "cook",
  min_protein_g: 40,
  max_kcal: 700,
  max_budget_aud: 10,
  min_kcal: 350,
  dairy_free: false,
  preference: "",
};

function loadTargets(): TargetFormState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULTS;
    return { ...DEFAULTS, ...JSON.parse(raw) };
  } catch {
    return DEFAULTS;
  }
}

function toRequest(targets: TargetFormState, excludeIds: string[]): MealRequest {
  return {
    meal_type: targets.meal_type,
    mode: targets.mode,
    min_protein_g: targets.min_protein_g,
    max_kcal: targets.max_kcal,
    max_budget_aud: targets.max_budget_aud,
    min_kcal: targets.min_kcal,
    dairy_free: targets.dairy_free,
    preference: targets.preference.trim() ? targets.preference.trim() : null,
    exclude_ids: excludeIds,
  };
}

export default function App() {
  const [targets, setTargets] = useState<TargetFormState>(loadTargets);
  const [excludeIds, setExcludeIds] = useState<string[]>([]);
  const [meal, setMeal] = useState<Meal | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [healthWarning, setHealthWarning] = useState<string | null>(null);

  const invalidMinKcal =
    targets.min_kcal != null && targets.min_kcal >= targets.max_kcal;

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(targets));
  }, [targets]);

  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      // API can take a while to finish loading the embedding model on first boot
      for (let attempt = 1; attempt <= 6; attempt++) {
        try {
          const h = await checkHealth();
          if (cancelled) return;
          if (h.ready) {
            setHealthWarning(null);
            return;
          }
          const bits: string[] = [];
          if (!h.mongo.ok) bits.push("MongoDB");
          if (!h.gemini.api_key_configured) bits.push("Gemini API key");
          if (h.mongo.ok && h.mongo.products_with_embeddings === 0) bits.push("embeddings");
          setHealthWarning(`API degraded: ${bits.join(", ") || h.status}`);
          return;
        } catch {
          if (cancelled) return;
          if (attempt === 6) {
            setHealthWarning("API unreachable — start uvicorn on port 8000");
            return;
          }
          await new Promise((r) => setTimeout(r, 1500 * attempt));
        }
      }
    };
    void run();
    return () => {
      cancelled = true;
    };
  }, []);

  const runGenerate = async (ids: string[], resetExcludes: boolean) => {
    setLoading(true);
    setError(null);
    if (resetExcludes) setExcludeIds([]);
    try {
      const next = await generateMeal(toRequest(targets, ids));
      setMeal(next);
      if (!resetExcludes) setExcludeIds(ids);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  const onGenerate = () => runGenerate([], true);

  const onSomethingElse = () => {
    if (!meal) return;
    const ids = Array.from(new Set([...excludeIds, ...meal.items.map((i) => i.product_id)]));
    runGenerate(ids, false);
  };

  const onSwap = (productId: string) => {
    const ids = Array.from(new Set([...excludeIds, productId]));
    runGenerate(ids, false);
  };

  const resultKey = useMemo(() => meal?.title ?? "empty", [meal]);

  return (
    <div className="app-shell">
      <FoodParticleField />
      <header className="site-header">
        <h1>Macro Grocery</h1>
        <p>One Australian meal matched to protein, calories, and budget.</p>
      </header>

      {healthWarning && <div className="banner warn">{healthWarning}</div>}
      {error && <div className="banner error">{error}</div>}
      {loading && <div className="banner info">Generating meal… this can take a few seconds.</div>}

      <main className="layout">
        <div className="center-stage">
          <TargetForm
            value={targets}
            onChange={setTargets}
            onGenerate={onGenerate}
            loading={loading}
            invalidMinKcal={invalidMinKcal}
          />
        </div>

        {meal && (
          <div className="results" key={resultKey}>
            <MacroBars meal={meal} targets={targets} />
            <MealCard
              meal={meal}
              loading={loading}
              onSwap={onSwap}
              onSomethingElse={onSomethingElse}
            />
            <ShoppingList items={meal.shopping_list} />
          </div>
        )}
      </main>
    </div>
  );
}
