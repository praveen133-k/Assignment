from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.service import generate_otp, store_otp, verify_otp, create_jwt_token
from app.models import User
from sqlalchemy.future import select

router = APIRouter(prefix="/auth", tags=["auth"])

class SignupRequest(BaseModel):
    mobile: str
    password: str | None = None

class OTPRequest(BaseModel):
    mobile: str

class VerifyOTPRequest(BaseModel):
    mobile: str
    otp: str

class ForgotPasswordRequest(BaseModel):
    mobile: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

@router.post("/signup")
async def signup(data: SignupRequest, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(User.mobile == data.mobile))
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(mobile=data.mobile)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"message": "User registered"}

@router.post("/send-otp")
async def send_otp(data: OTPRequest, db: AsyncSession = Depends(get_db)):
    # Generate and store OTP
    otp = generate_otp()
    store_otp(data.mobile, otp)
    return {"otp": otp}

@router.post("/verify-otp")
async def verify_otp_endpoint(data: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    # Verify OTP
    if not verify_otp(data.mobile, data.otp):
        raise HTTPException(status_code=400, detail="Invalid OTP")
    # Find user
    result = await db.execute(select(User).where(User.mobile == data.mobile))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = create_jwt_token(user.id)
    return {"token": token}

@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    # Generate and store OTP for password reset
    otp = generate_otp()
    store_otp(data.mobile, otp)
    return {"otp": otp}

@router.post("/change-password")
async def change_password(data: ChangePasswordRequest, db: AsyncSession = Depends(get_db)):
    # Placeholder: implement password change logic
    return {"message": "Password changed (mock)"} 