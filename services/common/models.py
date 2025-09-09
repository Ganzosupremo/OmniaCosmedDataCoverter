"""Database models for Phase Analyzer SaaS."""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"
    TEAM = "team"


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"

    def __init__(self, name, email, plan, stripe_customer_id, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.email = email
        self.stripe_customer_id = stripe_customer_id
        self.plan = plan

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    stripe_customer_id = Column(String(255), unique=True, nullable=True)
    plan = Column(String(50), default=PlanType.FREE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    jobs = relationship("Job", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stripe_subscription_id = Column(String(255), unique=True, nullable=False)
    plan = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)  # active, canceled, past_due, etc.
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="subscriptions")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(String(255), unique=True, index=True, nullable=False)  # RQ job ID
    status = Column(String(50), default=JobStatus.PENDING)
    file_count = Column(Integer, nullable=False)
    total_size_mb = Column(Float, nullable=False)
    input_files = Column(Text, nullable=True)  # JSON array of file names
    output_url = Column(String(500), nullable=True)  # S3 download URL
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="jobs")
