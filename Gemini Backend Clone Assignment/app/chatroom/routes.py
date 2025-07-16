from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth.service import decode_jwt_token
from app.models import Chatroom, Message, User, Subscription
from sqlalchemy.future import select
from pydantic import BaseModel
from app.core.cache import cache_chatrooms, get_cached_chatrooms, invalidate_chatroom_cache
from app.chatroom.tasks import gemini_respond
from app.core.rate_limit import check_rate_limit, increment_rate_limit, BASIC_DAILY_LIMIT

router = APIRouter(prefix="/chatroom", tags=["chatroom"])

class ChatroomCreateRequest(BaseModel):
    name: str

class MessageRequest(BaseModel):
    content: str

# Helper to get user from JWT
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

async def get_user_subscription(user: User, db: AsyncSession):
    result = await db.execute(select(Subscription).where(Subscription.user_id == user.id))
    sub = result.scalar_one_or_none()
    return sub.tier if sub else 'basic'

@router.post("")
async def create_chatroom(data: ChatroomCreateRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    chatroom = Chatroom(user_id=user.id, name=data.name)
    db.add(chatroom)
    await db.commit()
    await db.refresh(chatroom)
    invalidate_chatroom_cache(user.id)
    return {"chatroom": {"id": chatroom.id, "name": chatroom.name}}

@router.get("")
async def list_chatrooms(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    cached = get_cached_chatrooms(user.id)
    if cached is not None:
        return {"chatrooms": cached, "cached": True}
    result = await db.execute(select(Chatroom).where(Chatroom.user_id == user.id))
    chatrooms = result.scalars().all()
    chatroom_list = [{"id": c.id, "name": c.name} for c in chatrooms]
    cache_chatrooms(user.id, chatroom_list)
    return {"chatrooms": chatroom_list, "cached": False}

@router.get("/{chatroom_id}")
async def get_chatroom(chatroom_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Chatroom).where(Chatroom.id == chatroom_id).where(Chatroom.user_id == user.id)
    )
    chatroom = result.scalar_one_or_none()
    if chatroom is None:
        raise HTTPException(status_code=404, detail="Chatroom not found")
    return {"chatroom": {"id": chatroom.id, "name": chatroom.name}}

@router.post("/{chatroom_id}/message")
async def send_message(chatroom_id: int, data: MessageRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # Rate limit for Basic users
    tier = await get_user_subscription(user, db)
    if tier == 'basic':
        count = check_rate_limit(user.id)
        if count >= BASIC_DAILY_LIMIT:
            raise HTTPException(status_code=429, detail="Daily message limit reached for Basic tier.")
        increment_rate_limit(user.id)
    # Enqueue Gemini API call via Celery
    task = gemini_respond.delay(data.content)
    response = task.get(timeout=10)  # In production, use async result polling or WebSocket
    message = Message(chatroom_id=chatroom_id, user_id=user.id, content=data.content, response=response)
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return {"message": {"id": message.id, "content": message.content, "response": message.response}} 