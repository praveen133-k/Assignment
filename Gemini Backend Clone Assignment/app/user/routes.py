from fastapi import APIRouter, Depends, Header, HTTPException, status
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.service import decode_jwt_token
from app.models import User
from sqlalchemy.future import select

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/me")
async def get_me(Authorization: str = Header(...), db: AsyncSession = Depends(get_db)):
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
    return {"user": {"id": user.id, "mobile": user.mobile, "tier": getattr(user, 'tier', 'basic')}} 