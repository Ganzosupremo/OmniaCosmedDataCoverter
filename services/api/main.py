"""Minimal FastAPI application for Phase Analyzer SaaS."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from services.common.config import get_plan_limits


app = FastAPI(title="Phase Analyzer API")


class EntitlementResponse(BaseModel):
    max_files: int
    max_mb: int
    batch: bool


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/entitlements/{plan}", response_model=EntitlementResponse)
def entitlements(plan: str) -> EntitlementResponse:
    """Return plan limits for the given subscription tier."""
    try:
        limits = get_plan_limits(plan)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return EntitlementResponse(**limits.__dict__)
