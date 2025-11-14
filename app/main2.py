# app/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import uuid

from app.core.conversation.orchastrator import ConversationOrchestrator, OrchestratorResponse
from app.core.agentic_layer.tools.feedback_tool import FeedbackTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agentic Chatbot API",
    description="Next-generation chatbot with RAG, tools, and multi-turn conversations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator = ConversationOrchestrator()
feedback_tool = FeedbackTool()


# ===== Request/Response Models =====

class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "message": "I want to book a vehicle",
                "session_id": "session_abc"
            }
        }


class ChatResponse(BaseModel):
    message: str
    response_type: str
    intent: str
    confidence: float
    session_id: str
    requires_followup: bool = False
    next_step: Optional[str] = None
    metadata: Dict[str, Any] = {}


class FeedbackRequest(BaseModel):
    user_id: str
    session_id: str
    rating: Optional[int] = None
    sentiment: Optional[str] = None
    comment: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "session_id": "session_abc",
                "rating": 5,
                "sentiment": "positive",
                "comment": "Very helpful!"
            }
        }


# ===== API Endpoints =====

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Agentic Chatbot API",
        "version": "1.0.0"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint

    Handles:
    - Intent classification (PyTorch model)
    - FAQ retrieval (RAG)
    - Tool execution
    - Multi-turn conversations
    """

    try:
        logger.info(f"Processing message from user {request.user_id}: {request.message}")

        # Process message through orchestrator
        response: OrchestratorResponse = await orchestrator.process_message(
            user_id=request.user_id,
            message=request.message,
            session_id=request.session_id
        )

        # Get session ID from state
        state = orchestrator.state_manager.get_or_create_state(
            request.user_id,
            request.session_id
        )

        return ChatResponse(
            message=response.message,
            response_type=response.response_type.value,
            intent=response.intent,
            confidence=response.confidence,
            session_id=state.session_id,
            requires_followup=response.requires_followup,
            next_step=response.next_step,
            metadata=response.metadata
        )

    except Exception as e:
        logger.error(f"Error processing chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@app.post("/feedback")
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


@app.get("/feedback/stats")
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


@app.get("/session/{user_id}")
async def get_user_sessions(user_id: str):
    """
    Get all sessions for a user
    """

    try:
        sessions = orchestrator.state_manager.get_user_sessions(user_id)
        return {
            "user_id": user_id,
            "sessions": sessions,
            "total": len(sessions)
        }

    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session/{user_id}/{session_id}")
async def get_session_state(user_id: str, session_id: str):
    """
    Get conversation state for a specific session
    """

    try:
        state = orchestrator.state_manager.get_or_create_state(user_id, session_id)
        return state.to_dict()

    except Exception as e:
        logger.error(f"Error getting session state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/session/{user_id}/{session_id}")
async def delete_session(user_id: str, session_id: str):
    """
    Delete a conversation session
    """

    try:
        orchestrator.state_manager.delete_state(user_id, session_id)
        return {
            "status": "success",
            "message": f"Session {session_id} deleted"
        }

    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)