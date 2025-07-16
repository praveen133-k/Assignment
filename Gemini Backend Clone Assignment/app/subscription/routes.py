from fastapi import APIRouter, Depends, Request, Header, HTTPException, status, BackgroundTasks
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.service import decode_jwt_token
from app.models import User, Subscription
from sqlalchemy.future import select
import stripe
from app.core.config import settings
import os

router = APIRouter(prefix="/subscription", tags=["subscription"])

stripe.api_key = settings.STRIPE_SECRET_KEY

STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "price_1N...mock")  # Set your real price ID here
DOMAIN = os.getenv("DOMAIN", "http://localhost:8000")

async def get_current_user(Authorization: str = Header(...), db: AsyncSession = Depends(get_db)):
    if not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    token = Authorization.split(" ", 1)[1]
    payload = decode_jwt_token(token)
    if not payload or "user_id" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload["user_id"]
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/pro")
async def subscribe_pro(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Create Stripe customer if not present
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(phone=user.mobile)
        user.stripe_customer_id = customer.id
        await db.commit()
        await db.refresh(user)
    # Create Stripe Checkout session
    session = stripe.checkout.Session.create(
        customer=user.stripe_customer_id,
        payment_method_types=["card"],
        line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
        mode="subscription",
        success_url=f"{DOMAIN}/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{DOMAIN}/cancel",
    )
    return {"checkout_url": session.url}

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")
    # Handle event types
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id = session["customer"]
        # Find user by Stripe customer ID
        result = await db.execute(select(User).where(User.stripe_customer_id == customer_id))
        user = result.scalar_one_or_none()
        if user:
            # Set subscription to pro
            result = await db.execute(select(Subscription).where(Subscription.user_id == user.id))
            sub = result.scalar_one_or_none()
            if not sub:
                sub = Subscription(user_id=user.id, tier="pro", status="active")
                db.add(sub)
            else:
                sub.tier = "pro"
                sub.status = "active"
            await db.commit()
    elif event["type"] in ["customer.subscription.deleted", "customer.subscription.canceled"]:
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        result = await db.execute(select(User).where(User.stripe_customer_id == customer_id))
        user = result.scalar_one_or_none()
        if user:
            result = await db.execute(select(Subscription).where(Subscription.user_id == user.id))
            sub = result.scalar_one_or_none()
            if sub:
                sub.tier = "basic"
                sub.status = "inactive"
                await db.commit()
    return {"status": "webhook processed"}

@router.get("/status")
async def subscription_status(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subscription).where(Subscription.user_id == user.id))
    sub = result.scalar_one_or_none()
    tier = sub.tier if sub else 'basic'
    return {"tier": tier} 