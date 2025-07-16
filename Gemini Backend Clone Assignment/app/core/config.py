import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")
    REDIS_URL: str | None = os.getenv("REDIS_URL")
    STRIPE_SECRET_KEY: str | None = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: str | None = os.getenv("STRIPE_WEBHOOK_SECRET")
    JWT_SECRET: str | None = os.getenv("JWT_SECRET")
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

settings = Settings() 