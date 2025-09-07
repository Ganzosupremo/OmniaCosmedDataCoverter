from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Phase Analyzer API")

class EntitlementResponse(BaseModel):
    max_files: int
    max_mb: int
    batch: bool


@app.get("/health")
async def health() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "ok"}


@app.get("/entitlements/{plan}", response_model=EntitlementResponse)
async def get_entitlements(plan: str = "free") -> EntitlementResponse:
    """Get user entitlements based on their subscription plan."""
    from services.common.config import get_plan_limits

    limits = get_plan_limits(plan)
    return EntitlementResponse(
        max_files=limits.max_files,
        max_mb=limits.max_mb,
        batch=limits.batch
    )  # services/api/main.py