from fastapi import FastAPI, Depends, HTTPException, status, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import os
import stripe
import json
import bcrypt
import time
from datetime import datetime
import uuid

from services.common.database import get_db, create_tables
from services.common.models import User, Job, Subscription, JobStatus
from services.common.schemas import (
    UserCreate, User as UserSchema, 
    JobCreate, Job as JobSchema,
    EntitlementResponse, JobSubmissionRequest, JobStatusResponse
)
from services.common.auth import get_current_user, check_plan_limits, create_access_token
from services.common.config import get_plan_limits

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

app = FastAPI(title="Phase Analyzer API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()


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
    )


# User Management Endpoints
@app.post("/users/", response_model=UserSchema)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create Stripe customer
    stripe_customer = stripe.Customer.create(
        email=user.email,
        name=user.name
    )
    
    # Create user in database
    db_user = User(
        email=user.email,
        name=user.name,
        stripe_customer_id=stripe_customer.id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@app.get("/users/me", response_model=UserSchema)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user


@app.get("/users/me/entitlements", response_model=EntitlementResponse)
async def get_user_entitlements(current_user: User = Depends(get_current_user)):
    """Get current user's plan entitlements."""
    limits = get_plan_limits(current_user.plan)
    return EntitlementResponse(
        max_files=limits.max_files,
        max_mb=limits.max_mb,
        batch=limits.batch
    )


# Job Management Endpoints
@app.post("/jobs/", response_model=JobSchema)
async def submit_job(
    job_request: JobSubmissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a new batch processing job."""
    from redis import Redis
    from rq import Queue
    
    # Calculate job requirements
    file_count = len(job_request.files)
    total_size_mb = sum([os.path.getsize(f) / (1024 * 1024) for f in job_request.files if os.path.exists(f)])
    
    # Check plan limits
    check_plan_limits(current_user, file_count, total_size_mb)
    
    # Create job record
    job_id = str(uuid.uuid4())
    db_job = Job(
        user_id=current_user.id,
        job_id=job_id,
        file_count=file_count,
        total_size_mb=total_size_mb,
        input_files=json.dumps(job_request.files),
        status=JobStatus.PENDING
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    # Queue job for processing
    redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
    redis = Redis.from_url(redis_url)
    queue = Queue(connection=redis)
    
    queue.enqueue(
        "process_batch_job",
        job_id,
        job_request.files,
        current_user.id,
        job_id=job_id
    )
    
    return db_job


@app.get("/jobs/", response_model=List[JobSchema])
async def get_user_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all jobs for the current user."""
    jobs = db.query(Job).filter(Job.user_id == current_user.id).order_by(Job.created_at.desc()).all()
    return jobs


@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get status of a specific job."""
    job = db.query(Job).filter(
        Job.job_id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        download_url=job.output_url,
        error_message=job.error_message
    )


# Stripe Webhook Endpoint
@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    if event["type"] == "customer.subscription.created":
        subscription = event["data"]["object"]
        handle_subscription_created(subscription, db)
    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        handle_subscription_updated(subscription, db)
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        handle_subscription_deleted(subscription, db)
    
    return {"status": "success"}


def handle_subscription_created(subscription_data: dict, db: Session):
    """Handle new subscription creation."""
    customer_id = subscription_data["customer"]
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    
    if user:
        # Determine plan from price_id
        price_id = subscription_data["items"]["data"][0]["price"]["id"]
        plan = get_plan_from_price_id(price_id)
        
        # Update user plan
        user.plan = plan
        
        # Create subscription record
        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id=subscription_data["id"],
            plan=plan,
            status=subscription_data["status"],
            current_period_start=datetime.fromtimestamp(subscription_data["current_period_start"]),
            current_period_end=datetime.fromtimestamp(subscription_data["current_period_end"])
        )
        
        db.add(subscription)
        db.commit()


def handle_subscription_updated(subscription_data: dict, db: Session):
    """Handle subscription updates."""
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_data["id"]
    ).first()
    
    if subscription:
        # Update subscription details
        subscription.status = subscription_data["status"]
        subscription.current_period_start = datetime.fromtimestamp(subscription_data["current_period_start"])
        subscription.current_period_end = datetime.fromtimestamp(subscription_data["current_period_end"])
        
        # Update user plan if subscription is active
        if subscription_data["status"] == "active":
            price_id = subscription_data["items"]["data"][0]["price"]["id"]
            plan = get_plan_from_price_id(price_id)
            subscription.user.plan = plan
        
        db.commit()


def handle_subscription_deleted(subscription_data: dict, db: Session):
    """Handle subscription cancellation."""
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_data["id"]
    ).first()
    
    if subscription:
        # Downgrade user to free plan
        subscription.user.plan = "free"
        subscription.status = "canceled"
        db.commit()


def get_plan_from_price_id(price_id: str) -> str:
    """Map Stripe price ID to plan name."""
    price_plan_mapping = {
        os.getenv("STRIPE_PRO_PRICE_ID"): "pro",
        os.getenv("STRIPE_TEAM_PRICE_ID"): "team",
    }
    return price_plan_mapping.get(price_id, "free")


# Test endpoints for development/testing without external API dependencies
@app.post("/test/create-user")
async def test_create_user(username: str, email: str, password: str, db: Session = Depends(get_db)):
    """Test endpoint to create user without Stripe integration."""
    try:
        # Check if user already exists
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user without Stripe customer creation
        user = User(
            name=username,
            email=email,
            plan="free",
            stripe_customer_id=f"test_cus_{username}_{int(time.time())}"  # Mock customer ID
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return {"message": "User created successfully", "user_id": user.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/test/upgrade-plan")
async def test_upgrade_plan(
    plan: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test endpoint to upgrade user plan without Stripe payment."""
    valid_plans = ["free", "pro", "team"]
    if plan not in valid_plans:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    # Update user plan directly
    current_user.plan = plan
    
    # Create mock subscription if upgrading to paid plan
    if plan != "free":
        subscription = Subscription(
            user_id=current_user.id,
            stripe_subscription_id=f"test_sub_{current_user.id}_{int(time.time())}",
            status="active",
            plan=plan
        )
        db.add(subscription)
    
    db.commit()
    
    return {"message": f"Plan upgraded to {plan}", "plan": plan}


@app.get("/test/simulate-webhook")
async def test_simulate_webhook(event_type: str, user_id: int, plan: str = "pro", db: Session = Depends(get_db)):
    """Test endpoint to simulate Stripe webhook events."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if event_type == "customer.subscription.created":
        # Simulate subscription creation
        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id=f"test_sub_{user.id}_{int(time.time())}",
            status="active",
            plan=plan
        )
        user.plan = plan
        db.add(subscription)
        db.commit()
        return {"message": "Subscription created", "plan": plan}
    
    elif event_type == "customer.subscription.deleted":
        # Simulate subscription cancellation
        subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
        if subscription:
            subscription.status = "canceled"
            user.plan = "free"
            db.commit()
        return {"message": "Subscription canceled", "plan": "free"}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid event type")


@app.get("/test/reset-limits")
async def test_reset_limits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test endpoint to reset user limits for testing."""
    current_user.files_processed_today = 0
    current_user.last_reset_date = datetime.utcnow().date()
    db.commit()
    
    return {"message": "Limits reset", "files_processed_today": 0}


@app.get("/test/user-status")
async def test_user_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Test endpoint to get comprehensive user status."""
    subscriptions = db.query(Subscription).filter(Subscription.user_id == current_user.id).all()
    
    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "plan": current_user.plan,
            "files_processed_today": current_user.files_processed_today,
            "last_reset_date": current_user.last_reset_date.isoformat() if current_user.last_reset_date else None,
            "stripe_customer_id": current_user.stripe_customer_id
        },
        "subscriptions": [
            {
                "id": sub.id,
                "stripe_subscription_id": sub.stripe_subscription_id,
                "status": sub.status,
                "plan": sub.plan,
                "created_at": sub.created_at.isoformat() if sub.created_at else None
            }
            for sub in subscriptions
        ]
    }