# chat.py
"""
Command-line interface for testing the agentic chatbot
"""
import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.orchestrator import ConversationOrchestrator


class ChatCLI:
    """Interactive CLI for testing chatbot"""

    def __init__(self):
        self.orchestrator = ConversationOrchestrator()
        self.user_id = "test_user"
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def print_banner(self):
        """Print welcome banner"""
        print("\n" + "=" * 60)
        print("🤖 AGENTIC CHATBOT - Interactive CLI")
        print("=" * 60)
        print(f"User ID: {self.user_id}")
        print(f"Session ID: {self.session_id}")
        print("\nCommands:")
        print("  - Type your message to chat")
        print("  - Type 'quit' or 'exit' to end session")
        print("  - Type 'history' to see conversation history")
        print("  - Type 'clear' to start new session")
        print("  - Type 'feedback' to give feedback")
        print("=" * 60 + "\n")

    def print_message(self, role: str, message: str, metadata: dict = None):
        """Print formatted message"""

        emoji_map = {
            "user": "👤",
            "assistant": "🤖",
            "system": "ℹ️"
        }

        emoji = emoji_map.get(role, "💬")
        print(f"\n{emoji} {role.upper()}: {message}")

        if metadata:
            print(f"   └─ Intent: {metadata.get('intent', 'N/A')} "
                  f"| Confidence: {metadata.get('confidence', 0):.2f} "
                  f"| Type: {metadata.get('response_type', 'N/A')}")

    async def handle_feedback(self):
        """Handle feedback collection"""

        print("\n📝 Please provide your feedback:")

        # Get rating
        while True:
            try:
                rating_input = input("Rating (1-5): ").strip()
                if not rating_input:
                    rating = None
                    break
                rating = int(rating_input)
                if 1 <= rating <= 5:
                    break
                print("Please enter a number between 1 and 5")
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 5")

        # Get sentiment
        sentiment = input("Sentiment (positive/neutral/negative): ").strip().lower()
        if sentiment not in ["positive", "neutral", "negative"]:
            sentiment = None

        # Get comment
        comment = input("Comment (optional): ").strip()
        if not comment:
            comment = None

        # Submit feedback
        from app.core.agentic_layer.tools.feedback_tool import FeedbackTool
        feedback_tool = FeedbackTool()

        result = feedback_tool._run(
            user_id=self.user_id,
            session_id=self.session_id,
            rating=rating,
            sentiment=sentiment,
            comment=comment
        )

        print(f"\n{result}")

    def show_history(self):
        """Show conversation history"""

        state = self.orchestrator.state_manager.get_or_create_state(
            self.user_id,
            self.session_id
        )

        if not state.messages:
            print("\n📭 No conversation history yet")
            return

        print("\n" + "=" * 60)
        print("📜 CONVERSATION HISTORY")
        print("=" * 60)

        for i, msg in enumerate(state.messages, 1):
            role = msg["role"]
            content = msg["content"]
            timestamp = msg.get("timestamp", "")

            emoji = "👤" if role == "user" else "🤖"
            print(f"\n{i}. {emoji} {role.upper()} [{timestamp}]")
            print(f"   {content}")

        print("=" * 60)

    def clear_session(self):
        """Start a new session"""

        self.orchestrator.state_manager.delete_state(self.user_id, self.session_id)
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"\n✨ New session started: {self.session_id}")

    async def run(self):
        """Main chat loop"""

        self.print_banner()

        try:
            while True:
                # Get user input
                user_input = input("\n👤 You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ['quit', 'exit']:
                    print("\n👋 Goodbye! Thanks for chatting!")
                    break

                elif user_input.lower() == 'history':
                    self.show_history()
                    continue

                elif user_input.lower() == 'clear':
                    self.clear_session()
                    continue

                elif user_input.lower() == 'feedback':
                    await self.handle_feedback()
                    continue

                # Process message
                try:
                    response = await self.orchestrator.process_message(
                        user_id=self.user_id,
                        message=user_input,
                        session_id=self.session_id
                    )

                    # Print response
                    self.print_message(
                        role="assistant",
                        message=response.message,
                        metadata={
                            "intent": response.intent,
                            "confidence": response.confidence,
                            "response_type": response.response_type.value
                        }
                    )

                    # Show follow-up hint if needed
                    if response.requires_followup:
                        print(f"\n💡 Tip: {response.next_step or 'Continue the conversation'}")

                except Exception as e:
                    print(f"\n❌ Error: {str(e)}")
                    import traceback
                    traceback.print_exc()

        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")

        except Exception as e:
            print(f"\n❌ Fatal error: {str(e)}")
            import traceback
            traceback.print_exc()


def main():
    """Entry point"""

    # Check if required environment variables are set
    import os
    if not os.environ.get("GITHUB_TOKEN"):
        print("⚠️  Warning: GITHUB_TOKEN environment variable not set")
        print("   The chatbot will have limited functionality\n")

    # Run chat CLI
    cli = ChatCLI()
    asyncio.run(cli.run())


if __name__ == "__main__":
    main()