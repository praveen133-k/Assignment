import httpx
from app.core.config import settings

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

async def get_gemini_response(prompt: str) -> str:
    headers = {"Authorization": f"Bearer {settings.GEMINI_API_KEY}"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    async with httpx.AsyncClient() as client:
        # Placeholder: return mock response
        # resp = await client.post(GEMINI_API_URL, headers=headers, json=payload)
        # return resp.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return "Gemini AI response (mock)" 