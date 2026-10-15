export type MealType = "breakfast" | "lunch" | "dinner" | "snack";
export type MealMode = "quick" | "cook";

export interface TargetFormState {
  meal_type: MealType;
  mode: MealMode;
  min_protein_g: number;
  max_kcal: number;
  max_budget_aud: number;
  min_kcal: number | null;
  dairy_free: boolean;
  preference: string;
}

export interface MealRequest {
  meal_type: MealType;
  mode: MealMode;
  min_protein_g: number;
  max_kcal: number;
  max_budget_aud: number;
  min_kcal: number | null;
  dairy_free: boolean;
  preference: string | null;
  exclude_ids: string[];
}

export interface MealItem {
  product_id: string;
  brand: string;
  product_name: string;
  category: string;
  grams: number;
  cost_aud: number;
  kcal: number;
  protein_g: number;
  fat_g: number;
  carbs_g: number;
}

export interface Totals {
  kcal: number;
  protein_g: number;
  fat_g: number;
  carbs_g: number;
  cost_aud: number;
}

export interface ShoppingItem {
  product_id: string;
  brand: string;
  product_name: string;
  size_g: number;
  pack_price_aud: number;
  packs: number;
}

export interface Meal {
  title: string;
  meal_type: string;
  mode: string;
  items: MealItem[];
  steps: string[];
  totals: Totals;
  unmet_targets: string[];
  shopping_list: ShoppingItem[];
}

export interface HealthResponse {
  status: string;
  ready: boolean;
  mongo: { ok: boolean; products_with_embeddings: number; error: string | null };
  gemini: { api_key_configured: boolean };
}
