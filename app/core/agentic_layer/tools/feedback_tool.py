# agentic_layer/tools/feedback_tool.py
from agentic_layer.tools import ReusableTool

class FeedbackTool(ReusableTool):
    name = "collect_feedback"
    description = "Collect user feedback and save it to a database or log."

    def _run(self, user_id: str, feedback_text: str) -> str:
        # TODO: Integrate with DB or analytics service
        print(f"📝 Feedback from {user_id}: {feedback_text}")
        return "✅ Thank you for your feedback!"
