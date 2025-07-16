from celery import Celery
from app.gemini.client import get_gemini_response
from app.core.config import settings

celery_app = Celery("worker", broker=settings.REDIS_URL)

@celery_app.task
def gemini_respond(prompt: str):
    # In production, use asyncio.run(get_gemini_response(prompt))
    # Here, just return a mock
    return f"Gemini AI response to: {prompt}" 