"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    plan: str
    stripe_customer_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubscriptionBase(BaseModel):
    plan: str
    status: str
    current_period_start: datetime
    current_period_end: datetime


class Subscription(SubscriptionBase):
    id: int
    user_id: int
    stripe_subscription_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobBase(BaseModel):
    file_count: int
    total_size_mb: float
    input_files: Optional[str] = None


class JobCreate(JobBase):
    input_files: List[str]  # List of input file paths


class Job(JobBase):
    id: int
    user_id: int
    job_id: str
    status: str
    output_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EntitlementResponse(BaseModel):
    max_files: int
    max_mb: int
    batch: bool


class JobSubmissionRequest(BaseModel):
    files: List[str]  # List of file paths/names


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: Optional[float] = None
    download_url: Optional[str] = None
    error_message: Optional[str] = None
