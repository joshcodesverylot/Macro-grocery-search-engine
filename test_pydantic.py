from pydantic import BaseModel, Field, ValidationError, field_validator
from google import genai
from google.genai import types
from dotenv import load_dotenv


load_dotenv()
class Ingredient(BaseModel):
    name: str
    quantity_grams: int = Field(description="Weight in grams as an integer")


class Recipe(BaseModel):
    title: str
    prep_time_minutes: int
    ingredients: list[Ingredient]
    instructions: list[str]


    # @field_validator('prep_time_minutes')
    # @classmethod
    # def enforce_ridiculous_prep_time(cls, v: int) -> int:
    #     if v != 999:
    #         raise ValueError(f"prep_time_minutes must be exactly 999, but got {v}")
    #     return v


class DailyMealPlan(BaseModel):
    plan_theme: str
    total_protein_grams: int
    total_calories: int
    recipes: list[Recipe]

client = genai.Client()
def generate_recipe_with_retries(prompt: str, max_retries: int = 3) -> Recipe:
    current_prompt = prompt

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}...")
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=current_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=DailyMealPlan,
                ),
            )
            
            # If the response parses cleanly, return the object immediately
            return DailyMealPlan.model_validate_json(response.text)
            
        except ValidationError as e:
            print(f"Validation failed on attempt {attempt + 1}. Retrying...")
            
            # Feed the exact Pydantic error trace back to the LLM
            current_prompt = (
                f"Original Request: {prompt}\n\n"
                f"Your previous attempt failed with this schema error:\n{e}\n\n"
                f"Please correct the output to strictly match the requested JSON schema."
            )
            
    raise Exception("LLM failed to generate valid structured data after maximum retries.")


# The final proof of concept
plan = generate_recipe_with_retries("Create a 2500 calorie meal plan using chicken, rice, and broccoli.")

print(f"Total Protein: {plan.total_protein_grams}g")
print(f"Meal 1: {plan.recipes[0].title}")
print(f"Meal 1, Ingredient 1: {plan.recipes[0].ingredients[0].name}")