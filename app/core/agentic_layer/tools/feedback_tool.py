# app/core/agentic_layer/tools/feedback_tool.py
from datetime import datetime
from typing import Dict, Any, Optional
import json
import os
from app.core.agentic_layer.tools.base_tool import ReusableTool
from app.config import settings


class FeedbackTool(ReusableTool):
    """Tool for collecting and storing user feedback"""

    name: str = "collect_feedback"
    description: str = (
        "Collect user feedback on conversation quality. "
        "Accepts rating (1-5), sentiment (positive/negative/neutral), "
        "and optional comment."
    )

    # Declare fields with type annotations and defaults so Pydantic recognizes them
    feedback_file: str = os.path.join(
        settings.BASE_DIR,
        "data",
        "feedback.json"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_feedback_file()

    def _ensure_feedback_file(self):
        """Create feedback file if it doesn't exist"""
        os.makedirs(os.path.dirname(self.feedback_file), exist_ok=True)
        if not os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'w') as f:
                pass  # Create empty file

    def _run(
            self,
            user_id: str,
            session_id: str,
            rating: Optional[int] = None,
            sentiment: Optional[str] = None,
            comment: Optional[str] = None,
            conversation_context: Optional[Dict] = None,
            **kwargs
    ) -> str:
        """Collect and store feedback"""

        # Validate rating
        if rating is not None and (rating < 1 or rating > 5):
            return "❌ Invalid rating. Please provide a rating between 1 and 5."

        # Validate sentiment
        valid_sentiments = ["positive", "negative", "neutral"]
        if sentiment and sentiment.lower() not in valid_sentiments:
            return f"❌ Invalid sentiment. Choose from: {', '.join(valid_sentiments)}"

        # Create feedback record
        feedback_record = {
            "feedback_id": f"FB{datetime.now().timestamp()}",
            "user_id": user_id,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "rating": rating,
            "sentiment": sentiment.lower() if sentiment else None,
            "comment": comment,
            "conversation_context": conversation_context or {}
        }

        # Save to file
        try:
            with open(self.feedback_file, 'a', encoding="utf-8") as f:
                f.write(json.dumps(feedback_record) + '\n')

            return self._format_success_message(feedback_record)

        except Exception as e:
            return f"❌ Failed to save feedback: {str(e)}"

    def _format_success_message(self, record: Dict) -> str:
        """Format success message"""

        message = "✅ Thank you for your feedback!\n\n"

        if record["rating"]:
            stars = "⭐" * record["rating"]
            message += f"Rating: {stars} ({record['rating']}/5)\n"

        if record["sentiment"]:
            emoji_map = {
                "positive": "😊",
                "neutral": "😐",
                "negative": "😞"
            }
            emoji = emoji_map.get(record["sentiment"], "")
            message += f"Sentiment: {emoji} {record['sentiment'].title()}\n"

        if record["comment"]:
            message += f"\nYour comment has been recorded."

        message += "\n\nYour feedback helps us improve our service!"

        return message

    def get_feedback_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get feedback statistics"""

        if not os.path.exists(self.feedback_file):
            return {"total": 0, "average_rating": 0}

        feedbacks = []

        try:
            with open(self.feedback_file, 'r', encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        feedback = json.loads(line)
                        if user_id is None or feedback["user_id"] == user_id:
                            feedbacks.append(feedback)
        except Exception as e:
            print(f"Error reading feedback: {e}")
            return {"error": str(e)}

        if not feedbacks:
            return {"total": 0, "average_rating": 0}

        # Calculate statistics
        ratings = [f["rating"] for f in feedbacks if f.get("rating")]
        sentiments = [f["sentiment"] for f in feedbacks if f.get("sentiment")]

        stats = {
            "total": len(feedbacks),
            "average_rating": sum(ratings) / len(ratings) if ratings else 0,
            "rating_distribution": self._count_occurrences(ratings),
            "sentiment_distribution": self._count_occurrences(sentiments),
            "with_comments": sum(1 for f in feedbacks if f.get("comment")),
        }

        return stats

    def _count_occurrences(self, items: list) -> Dict:
        """Count occurrences of items"""
        counts = {}
        for item in items:
            counts[item] = counts.get(item, 0) + 1
        return counts

    async def _arun(self, *args, **kwargs) -> str:
        """Async version"""
        raise NotImplementedError("Async feedback collection not implemented")
