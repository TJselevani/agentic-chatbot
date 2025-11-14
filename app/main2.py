# app/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any


from lib.logger.color_logger import setup_logger
logger = setup_logger(__name__)

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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)