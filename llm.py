import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from models import MealDraft

load_dotenv()
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

_client = None


def get_client():
    # Created on first use so importing this file (e.g. from api.py) doesn't need the key yet
    global _client
    if _client is None:
        if not os.getenv("GEMINI_API_KEY"):
            raise RuntimeError("GEMINI_API_KEY is not set: add it to the .env file next to llm.py")
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client


def draft_meal(prompt, system_instruction=None):
    """One Gemini call that must return a MealDraft.

    Raises pydantic.ValidationError if the reply doesn't fit the schema, and
    google.genai.errors.APIError on API problems (bad key, rate limit). planner.py decides what to retry.
    """
    response = get_client().models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_json_schema=MealDraft.model_json_schema(),
            temperature=0.7,
        ),
    )
    return MealDraft.model_validate_json(response.text)


if __name__ == "__main__":
    candidates = """id | name | category | per 100 g: kcal, protein g, price $
Coles|5 Star Extra Lean Beef Mince|500 | Extra Lean Beef Mince | Red meat | 129, 22.9, 1.80
Woolworths|Brushed Potatoes|2000 | Brushed Potatoes | Potatoes | 58, 2.3, 0.28
Coles|Broccoli|1000 | Broccoli | Other vegetables | 32, 4.0, 0.25
Coles|I'm Perfect Carrots Prepacked|1500 | Carrots | Orange/yellow vegetables | 35, 0.6, 0.13
Coles|Rice Puffs|360 | Rice Puffs | Breakfast cereal | 398, 7.2, 0.51"""
    prompt = (
        "Create one dinner using 3 to 6 of these products. Use the exact id values.\n"
        "Target: at least 40 g protein, at most 700 kcal.\n\n" + candidates
    )
    draft = draft_meal(prompt, system_instruction="You are a meal planner. Only use products from the list.")
    print(f"Model: {MODEL_NAME}")
    print(draft.model_dump_json(indent=2))
