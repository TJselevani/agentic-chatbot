from fastapi import APIRouter
from app.core.conversation.orchastrator import ConversationOrchestrator
from lib.logger.color_logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/session", tags=["Session"])

orchestrator = ConversationOrchestrator()


@router.get("/health")
async def health_check():
    """
    Detailed health check
    """

    return {
        "status": "healthy",
        "components": {
            "orchestrator": "ok",
            "agent_manager": "ok",
            "state_manager": "ok",
            "tools": len(orchestrator.tools)
        }
    }
