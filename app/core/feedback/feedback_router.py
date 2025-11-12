# app/feedback/feedback_router.py

from fastapi import APIRouter, Request
from app.core.feedback.feedback_store import save_feedback, get_feedback_summary

router = APIRouter()

@router.post("/feedback")
async def submit_feedback(request: Request):
    data = await request.json()
    user_id = data.get("user_id", "anonymous")
    session_id = data.get("session_id", "default")
    intent = data.get("intent")
    message = data.get("message")
    bot_response = data.get("bot_response")
    rating = data.get("rating")
    comment = data.get("comment", None)

    save_feedback(user_id, session_id, intent, message, bot_response, rating, comment)
    return {"status": "success", "message": "Feedback recorded. Thank you!"}


@router.get("/feedback/summary")
def feedback_summary():
    summary = get_feedback_summary()
    return {"feedback_summary": summary}
