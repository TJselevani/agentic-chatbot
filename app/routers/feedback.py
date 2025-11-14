from typing import Optional

from fastapi import APIRouter
from fastapi import HTTPException

from app.core.agentic_layer.tools.feedback_tool import FeedbackTool
from app.main2 import FeedbackRequest
from lib.logger.color_logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/feedback", tags=["Feedback"])

feedback_tool = FeedbackTool()


@router.post("/")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit user feedback
    """

    try:
        result = feedback_tool._run(
            user_id=request.user_id,
            session_id=request.session_id,
            rating=request.rating,
            sentiment=request.sentiment,
            comment=request.comment
        )

        return {
            "status": "success",
            "message": result
        }

    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_feedback_stats(user_id: Optional[str] = None):
    """
    Get feedback statistics
    """

    try:
        stats = feedback_tool.get_feedback_stats(user_id)
        return stats

    except Exception as e:
        logger.error(f"Error getting feedback stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
