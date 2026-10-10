"""
Thin FastAPI layer over planner.generate_meal.

Run:  uvicorn api:app --reload
Try:  http://127.0.0.1:8000/docs
"""
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google.genai import errors as genai_errors
from pymongo.errors import PyMongoError

from models import Meal, MealRequest
from planner import generate_meal
from retrieval import collection

load_dotenv()

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fail fast on a missing key so /docs isn't a surprise later
    if not os.getenv("GEMINI_API_KEY"):
        print("WARNING: GEMINI_API_KEY is not set in .env — /meals/generate will return 503")
    yield


app = FastAPI(title="Dynamic Macro & Grocery Engine", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Liveness + dependency checks. Always 200 if the process is up; `ok` is False if a dependency is down."""
    mongo_ok = False
    mongo_error = None
    try:
        collection.database.client.admin.command("ping")
        product_count = collection.count_documents({"embedding": {"$exists": True}})
        mongo_ok = True
    except PyMongoError as e:
        product_count = 0
        mongo_error = str(e)

    gemini_configured = bool(os.getenv("GEMINI_API_KEY"))
    ready = mongo_ok and gemini_configured and product_count > 0
    body = {
        "status": "ok" if ready else "degraded",
        "ready": ready,
        "mongo": {"ok": mongo_ok, "products_with_embeddings": product_count, "error": mongo_error},
        "gemini": {"api_key_configured": gemini_configured},
    }
    return body


@app.post("/meals/generate", response_model=Meal)
def meals_generate(request: MealRequest):
    """Generate one meal. Invalid bodies are rejected as 422 by FastAPI/Pydantic before this runs."""
    try:
        return generate_meal(request)
    except ValueError as e:
        # No candidates after filters / exclude_ids
        raise HTTPException(status_code=404, detail=str(e)) from e
    except RuntimeError as e:
        message = str(e)
        if "GEMINI_API_KEY" in message:
            raise HTTPException(
                status_code=503,
                detail="Gemini API key is not configured. Add GEMINI_API_KEY to .env and restart the server.",
            ) from e
        # Exhausted LLM retries with no usable draft
        raise HTTPException(status_code=502, detail=message) from e
    except genai_errors.ClientError as e:
        # Bad key, quota, bad request from Gemini
        code = getattr(e, "code", None) or 502
        if code in (401, 403):
            raise HTTPException(status_code=503, detail=f"Gemini rejected the API key: {e}") from e
        if code == 429:
            raise HTTPException(status_code=429, detail="Gemini rate limit hit. Wait a moment and try again.") from e
        raise HTTPException(status_code=502, detail=f"Gemini client error: {e}") from e
    except genai_errors.ServerError as e:
        raise HTTPException(status_code=502, detail=f"Gemini is unavailable: {e}") from e
    except genai_errors.APIError as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {e}") from e
    except PyMongoError as e:
        raise HTTPException(status_code=503, detail=f"MongoDB unavailable: {e}") from e


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Last resort so the UI always gets JSON, not a raw stack trace HTML page
    return JSONResponse(
        status_code=500,
        content={"detail": f"Unexpected server error: {type(exc).__name__}: {exc}"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
