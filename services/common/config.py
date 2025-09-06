"""Shared configuration and plan limits for Phase Analyzer SaaS."""

from dataclasses import dataclass
from typing import Dict
import os


@dataclass
class PlanLimits:
    max_files: int
    max_mb: int
    batch: bool


DEFAULT_PLAN_LIMITS: Dict[str, PlanLimits] = {
    "free": PlanLimits(max_files=1, max_mb=10, batch=False),
    "pro": PlanLimits(max_files=20, max_mb=150, batch=True),
    "team": PlanLimits(max_files=100, max_mb=1000, batch=True),
}


def get_plan_limits(plan: str) -> PlanLimits:
    """Fetch plan limits from environment or defaults."""
    plan = plan.lower()
    prefix = f"PLAN_{plan.upper()}_"
    try:
        max_files = int(os.getenv(prefix + "MAX_FILES", DEFAULT_PLAN_LIMITS[plan].max_files))
        max_mb = int(os.getenv(prefix + "MAX_MB", DEFAULT_PLAN_LIMITS[plan].max_mb))
        batch = os.getenv(prefix + "BATCH", str(DEFAULT_PLAN_LIMITS[plan].batch)).lower() == "true"
    except KeyError:
        raise ValueError(f"Unknown plan: {plan}")
    return PlanLimits(max_files=max_files, max_mb=max_mb, batch=batch)
