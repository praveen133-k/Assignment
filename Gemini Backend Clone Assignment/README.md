# Kuvaka Gemini-Style Backend

## Overview
A FastAPI backend supporting OTP-based authentication, user-specific chatrooms, Google Gemini-powered AI conversations, and Stripe-powered subscriptions.

## Tech Stack
- **Language:** Python (FastAPI)
- **Database:** PostgreSQL
- **Queue:** Celery (with Redis)
- **Cache:** Redis
- **Payments:** Stripe (sandbox)
- **External API:** Google Gemini
- **Auth:** JWT with OTP verification

## Setup

### 1. Clone the repo
```bash
# Already in your workspace
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env` and fill in your secrets:

```
DATABASE_URL=postgresql+asyncpg://postgres:8008281286Pp@@localhost:5432/kuvaka
REDIS_URL=redis://localhost:6379/0
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
JWT_SECRET=your_jwt_secret
GEMINI_API_KEY=your_gemini_api_key
```

### 4. Run Database Migrations
```bash
alembic upgrade head
```

### 5. Start Services
- Start Redis and PostgreSQL
- Start Celery worker:
```bash
celery -A app.worker worker --loglevel=info
```
- Start FastAPI app:
```bash
uvicorn app.main:app --reload
```

---

## Endpoints
See the API section in the project brief for all endpoints. 