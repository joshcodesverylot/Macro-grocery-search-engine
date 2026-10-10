from typing import Literal

from pydantic import BaseModel, Field, model_validator


# ==========================================
# INPUT: what the UI sends
# ==========================================
class MealRequest(BaseModel):
    meal_type: Literal["breakfast", "lunch", "dinner", "snack"]
    mode: Literal["quick", "cook"] = "cook"
    min_protein_g: float = Field(gt=0)
    max_kcal: float = Field(gt=0)
    max_budget_aud: float = Field(gt=0)
    # Stops the cheapest answer shrinking a dinner down to a snack
    min_kcal: float | None = Field(default=None, gt=0)
    dairy_free: bool = False
    preference: str | None = None
    exclude_ids: list[str] = []

    @model_validator(mode="after")
    def check_kcal_range(self):
        if self.min_kcal is not None and self.min_kcal >= self.max_kcal:
            raise ValueError("min_kcal must be less than max_kcal")
        return self


# ==========================================
# LLM OUTPUT: the schema Gemini must follow
# ==========================================
class DraftItem(BaseModel):
    product_id: str
    suggested_grams: float = Field(gt=0, le=1000)


class MealDraft(BaseModel):
    title: str
    items: list[DraftItem] = Field(min_length=3, max_length=6)
    steps: list[str]


# ==========================================
# OUTPUT: what the API returns to the UI
# ==========================================
class MealItem(BaseModel):
    product_id: str
    brand: str
    product_name: str
    category: str
    grams: float
    cost_aud: float
    kcal: float
    protein_g: float
    fat_g: float
    carbs_g: float


class Totals(BaseModel):
    kcal: float
    protein_g: float
    fat_g: float
    carbs_g: float
    cost_aud: float


class ShoppingItem(BaseModel):
    product_id: str
    brand: str
    product_name: str
    size_g: float
    pack_price_aud: float
    packs: int


class Meal(BaseModel):
    title: str
    meal_type: str
    mode: str
    items: list[MealItem]
    steps: list[str]
    totals: Totals
    # Empty when every target is met; otherwise human-readable reasons shown in the UI
    unmet_targets: list[str] = []
    shopping_list: list[ShoppingItem]
