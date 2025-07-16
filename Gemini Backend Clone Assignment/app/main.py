from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.routes import router as auth_router
from app.user.routes import router as user_router
from app.chatroom.routes import router as chatroom_router
from app.subscription.routes import router as subscription_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(chatroom_router)
app.include_router(subscription_router)

@app.get("/")
def root():
    return {"message": "Kuvaka Gemini Backend is running."} 