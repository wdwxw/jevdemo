"""TypeSafe 可视化 Demo 的 HTTP 服务。"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

APP_DIR = Path(__file__).parent
load_dotenv(APP_DIR / ".env")
app = FastAPI(title="TypeSafe System One Demo", version="1.0.0")


class EvaluateRequest(BaseModel):
    state: str = Field(min_length=1, max_length=100_000)
    custom_question: str | None = Field(default=None, max_length=500)
    model: str | None = Field(default=None, max_length=100)


PRESETS = {
    "urgent": "Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing. I'm losing sales. Please help ASAP.",
    "calm": "Could you explain how I can update the billing email on my account? There is no rush.",
    "angry": "This is the third time your payment integration has failed. You keep charging me and nobody has fixed it. Refund me now.",
}


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(APP_DIR / "static" / "index.html")


@app.get("/api/presets")
def presets() -> dict[str, str]:
    return PRESETS


@app.post("/api/evaluate")
def evaluate(request: EvaluateRequest) -> dict[str, Any]:
    if not os.getenv("TYPESAFE_API_KEY", "").strip():
        raise HTTPException(status_code=500, detail="服务端未配置 TYPESAFE_API_KEY")
    try:
        questions: dict[str, Any] = {
            "department": Choice(
                instructions="Which team should handle this request?",
                criteria={
                    "billing": "Payments, subscriptions, invoices, or refunds",
                    "technical": "Bugs, outages, or integration problems",
                    "sales": "Pricing, upgrades, or new-account questions",
                },
            ),
            "frustration": Score(
                instructions="How frustrated does the customer appear?",
                criteria=[
                    "Calm and only stating facts",
                    "Frustrated but civil",
                    "Very angry or using strong language",
                ],
            ),
            "is_urgent": Noul(
                instructions="Does the message convey urgency or time-sensitivity?",
            ),
        }
        if request.custom_question and request.custom_question.strip():
            questions["custom_judgment"] = Noul(
                instructions=request.custom_question.strip()
            )

        with TypeSafeClient(
            model=request.model or os.getenv("TYPESAFE_DEFAULT_MODEL", "jev-latest")
        ) as client:
            result = client.system_one(state=request.state, questions=questions)
            return result.raw_http_response.json()
    except Exception as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
