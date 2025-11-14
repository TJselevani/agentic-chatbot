# app/core/orchestrator.py
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from app.core.intent_layer.intent_classifier_2 import get_intent_with_confidence
from app.core.agentic_layer.agent_manager import AgentManager
from app.core.agentic_layer.tool_registry import get_registered_tools
from app.core.rag_layer.rag_engine import handle_faq
from app.core.conversation.conversation_manager import ConversationStateManager, ConversationState

logger = logging.getLogger(__name__)


class ResponseType(Enum):
    """Types of responses the system can generate"""
    DIRECT = "direct"  # Direct answer from intent classifier
    RAG = "rag"  # Answer from RAG system
    AGENT = "agent"  # Answer from AI agent
    TOOL = "tool"  # Tool execution result
    MULTI_TURN = "multi_turn"  # Multi-turn conversation flow


@dataclass
class OrchestratorResponse:
    """Standardized response from orchestrator"""
    message: str
    response_type: ResponseType
    intent: str
    confidence: float
    metadata: Dict = field(default_factory=dict)
    requires_followup: bool = False
    next_step: Optional[str] = None


class ConversationOrchestrator:
    """
    Main orchestrator that coordinates between:
    - PyTorch Intent Classifier
    - AI Agents (Azure/GPT/etc)
    - RAG System
    - Tools
    - Multi-turn conversation flows
    """

    def __init__(self):
        self.agent_manager = AgentManager()
        self.tools = {tool.name: tool for tool in get_registered_tools()}
        self.state_manager = ConversationStateManager()

        # Intent to handler mapping
        self.intent_handlers = {
            "faq": self._handle_faq,
            "booking": self._handle_booking,
            "payment": self._handle_payment,
            "weather": self._handle_weather,
            "general": self._handle_general,
        }

        logger.info(f"🚀 Orchestrator initialized with {len(self.tools)} tools")

    async def process_message(
            self,
            user_id: str,
            message: str,
            session_id: Optional[str] = None
    ) -> OrchestratorResponse:
        """
        Main entry point for processing user messages

        Flow:
        1. Check if in multi-turn conversation
        2. Get intent from PyTorch classifier
        3. If low confidence, verify with AI agent
        4. Route to appropriate handler
        5. Execute action (RAG, Tool, Multi-turn)
        6. Return response
        """

        # Step 1: Get or create conversation state
        state = self.state_manager.get_or_create_state(user_id, session_id)
        state.add_message("user", message)

        # Step 2: Check if in active multi-turn flow
        if state.is_in_flow():
            logger.info(f"📝 Continuing multi-turn flow: {state.current_flow}")
            return await self._handle_multi_turn(state, message)

        # Step 3: Get intent from PyTorch classifier
        intent_result = get_intent_with_confidence(message)
        intent = intent_result["intent"]
        confidence = intent_result["confidence"]
        high_confidence = intent_result["high_confidence"]

        logger.info(
            f"🎯 Intent: {intent} (confidence: {confidence:.2f}, "
            f"high: {high_confidence})"
        )

        # Step 4: If low confidence, verify with AI agent
        if not high_confidence:
            logger.info("🤔 Low confidence, verifying with AI agent...")
            intent, confidence = await self._verify_intent_with_agent(
                message, intent_result
            )

        # Step 5: Route to appropriate handler
        handler = self.intent_handlers.get(intent, self._handle_general)
        response = await handler(state, message, intent, confidence)

        # Step 6: Save state and return
        state.add_message("assistant", response.message)
        self.state_manager.save_state(state)

        return response

    async def _verify_intent_with_agent(
            self,
            message: str,
            intent_result: Dict
    ) -> tuple[str, float]:
        """Use AI agent to verify and refine intent when confidence is low"""

        prompt = f"""Analyze the user's message and determine their intent.

User message: "{message}"

PyTorch classifier suggests: {intent_result['intent']} (confidence: {intent_result['confidence']:.2f})
All probabilities: {intent_result['all_probabilities']}

Based on this message, what is the user's primary intent? Choose from:
- faq: Questions about services, pricing, policies
- booking: Vehicle booking or reservation requests
- payment: Payment inquiries or money transfers
- weather: Weather-related questions
- general: General conversation, greetings, chitchat

Respond with ONLY the intent label and a confidence score (0-1), formatted as:
INTENT: <label>
CONFIDENCE: <score>
REASONING: <brief explanation>"""

        try:
            agent = self.agent_manager.get_agent("azure")
            result = agent.run(prompt)

            # Parse agent response
            lines = result.strip().split('\n')
            refined_intent = None
            refined_confidence = 0.5

            for line in lines:
                if line.startswith("INTENT:"):
                    refined_intent = line.split(":", 1)[1].strip().lower()
                elif line.startswith("CONFIDENCE:"):
                    try:
                        refined_confidence = float(line.split(":", 1)[1].strip())
                    except:
                        refined_confidence = 0.7

            if refined_intent and refined_intent in self.intent_handlers:
                logger.info(f"✅ Agent refined intent: {refined_intent} ({refined_confidence:.2f})")
                return refined_intent, refined_confidence
            else:
                # Fall back to original
                return intent_result["intent"], intent_result["confidence"]

        except Exception as e:
            logger.error(f"❌ Agent verification failed: {e}")
            return intent_result["intent"], intent_result["confidence"]

    async def _handle_faq(
            self,
            state: ConversationState,
            message: str,
            intent: str,
            confidence: float
    ) -> OrchestratorResponse:
        """Handle FAQ questions using RAG"""

        logger.info("📚 Handling FAQ with RAG system...")

        try:
            # Get answer from RAG
            rag_answer = handle_faq(message)

            # If RAG doesn't have good answer, use agent
            if "don't have that information" in rag_answer.lower() or len(rag_answer) < 20:
                logger.info("🤖 RAG insufficient, using agent...")
                agent = self.agent_manager.get_agent("azure")
                agent_answer = agent.run(
                    f"Answer this FAQ question professionally: {message}"
                )

                return OrchestratorResponse(
                    message=agent_answer,
                    response_type=ResponseType.AGENT,
                    intent=intent,
                    confidence=confidence,
                    metadata={"source": "agent_fallback"}
                )

            return OrchestratorResponse(
                message=rag_answer,
                response_type=ResponseType.RAG,
                intent=intent,
                confidence=confidence,
                metadata={"source": "rag"}
            )

        except Exception as e:
            logger.error(f"❌ FAQ handling error: {e}")
            return self._error_response(intent, confidence)

    async def _handle_booking(
            self,
            state: ConversationState,
            message: str,
            intent: str,
            confidence: float
    ) -> OrchestratorResponse:
        """Handle vehicle booking with multi-turn conversation"""

        logger.info("🚗 Starting booking flow...")

        # Initialize booking flow
        state.start_flow("booking", {
            "vehicle_type": None,
            "pickup_location": None,
            "dropoff_location": None,
            "date": None,
            "time": None,
        })

        # Try to extract info from initial message
        agent = self.agent_manager.get_agent("azure")
        extraction_prompt = f"""Extract booking details from this message: "{message}"

Return in this exact format:
VEHICLE_TYPE: <type or "unknown">
PICKUP: <location or "unknown">
DROPOFF: <location or "unknown">
DATE: <date or "unknown">
TIME: <time or "unknown">

Only extract information that is explicitly mentioned."""

        result = agent.run(extraction_prompt)

        # Parse extracted info
        for line in result.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace('_', ' ')
                value = value.strip()

                if value.lower() != "unknown":
                    if "vehicle" in key:
                        state.flow_data["vehicle_type"] = value
                    elif "pickup" in key:
                        state.flow_data["pickup_location"] = value
                    elif "dropoff" in key:
                        state.flow_data["dropoff_location"] = value
                    elif "date" in key:
                        state.flow_data["date"] = value
                    elif "time" in key:
                        state.flow_data["time"] = value

        # Determine what to ask next
        next_question = self._get_next_booking_question(state.flow_data)

        if next_question:
            return OrchestratorResponse(
                message=next_question,
                response_type=ResponseType.MULTI_TURN,
                intent=intent,
                confidence=confidence,
                requires_followup=True,
                next_step="collect_booking_info",
                metadata={"flow": "booking", "collected": state.flow_data}
            )
        else:
            # All info collected, confirm booking
            return await self._confirm_booking(state, intent, confidence)

    def _get_next_booking_question(self, data: Dict) -> Optional[str]:
        """Determine next question in booking flow"""

        if not data.get("vehicle_type"):
            return "🚗 What type of vehicle would you like to book? (sedan, SUV, van, etc.)"
        elif not data.get("pickup_location"):
            return "📍 Where should we pick you up?"
        elif not data.get("dropoff_location"):
            return "📍 Where would you like to go?"
        elif not data.get("date"):
            return "📅 What date do you need the vehicle? (e.g., tomorrow, Dec 25, etc.)"
        elif not data.get("time"):
            return "🕐 What time should we pick you up?"

        return None  # All info collected

    async def _confirm_booking(
            self,
            state: ConversationState,
            intent: str,
            confidence: float
    ) -> OrchestratorResponse:
        """Confirm and execute booking"""

        data = state.flow_data
        confirmation = f"""📋 **Booking Summary**

🚗 Vehicle: {data['vehicle_type']}
📍 Pickup: {data['pickup_location']}
📍 Dropoff: {data['dropoff_location']}
📅 Date: {data['date']}
🕐 Time: {data['time']}

Would you like to confirm this booking? (yes/no)"""

        state.flow_step = "awaiting_confirmation"

        return OrchestratorResponse(
            message=confirmation,
            response_type=ResponseType.MULTI_TURN,
            intent=intent,
            confidence=confidence,
            requires_followup=True,
            next_step="confirm_booking",
            metadata={"flow": "booking", "step": "confirmation"}
        )

    async def _handle_payment(
            self,
            state: ConversationState,
            message: str,
            intent: str,
            confidence: float
    ) -> OrchestratorResponse:
        """Handle payment and money transfer"""

        logger.info("💰 Starting payment flow...")

        # Similar multi-turn flow as booking
        state.start_flow("payment", {
            "amount": None,
            "recipient": None,
            "method": None,
        })

        return OrchestratorResponse(
            message="💳 I can help you with payments. How much would you like to send?",
            response_type=ResponseType.MULTI_TURN,
            intent=intent,
            confidence=confidence,
            requires_followup=True,
            next_step="collect_payment_info",
            metadata={"flow": "payment"}
        )

    async def _handle_weather(
            self,
            state: ConversationState,
            message: str,
            intent: str,
            confidence: float
    ) -> OrchestratorResponse:
        """Handle weather queries using weather tool"""

        logger.info("🌤️ Handling weather query with tool...")

        # Extract city from message
        agent = self.agent_manager.get_agent("azure")
        city_prompt = f"Extract the city name from this message: '{message}'. Reply with ONLY the city name, nothing else."
        city = agent.run(city_prompt).strip()

        # Use weather tool
        if "get_weather" in self.tools:
            weather_tool = self.tools["get_weather"]
            result = weather_tool._run(city)

            return OrchestratorResponse(
                message=result,
                response_type=ResponseType.TOOL,
                intent=intent,
                confidence=confidence,
                metadata={"tool": "get_weather", "city": city}
            )

        return self._error_response(intent, confidence)

    async def _handle_general(
            self,
            state: ConversationState,
            message: str,
            intent: str,
            confidence: float
    ) -> OrchestratorResponse:
        """Handle general conversation"""

        logger.info("💬 Handling general conversation...")

        agent = self.agent_manager.get_agent("azure")
        response = agent.run(message)

        return OrchestratorResponse(
            message=response,
            response_type=ResponseType.AGENT,
            intent=intent,
            confidence=confidence,
            metadata={"source": "agent"}
        )

    async def _handle_multi_turn(
            self,
            state: ConversationState,
            message: str
    ) -> OrchestratorResponse:
        """Handle ongoing multi-turn conversations"""

        flow = state.current_flow

        if flow == "booking":
            return await self._continue_booking_flow(state, message)
        elif flow == "payment":
            return await self._continue_payment_flow(state, message)

        # Unknown flow, end it
        state.end_flow()
        return await self.process_message(state.user_id, message, state.session_id)

    async def _continue_booking_flow(
            self,
            state: ConversationState,
            message: str
    ) -> OrchestratorResponse:
        """Continue booking multi-turn flow"""

        # Check if awaiting confirmation
        if state.flow_step == "awaiting_confirmation":
            if message.lower() in ["yes", "y", "confirm", "ok", "sure"]:
                # Execute booking via tool
                if "vehicle_booking" in self.tools:
                    tool = self.tools["vehicle_booking"]
                    result = tool._run(**state.flow_data)
                    state.end_flow()

                    return OrchestratorResponse(
                        message=f"✅ {result}",
                        response_type=ResponseType.TOOL,
                        intent="booking",
                        confidence=1.0,
                        metadata={"booking_completed": True}
                    )
                else:
                    state.end_flow()
                    return OrchestratorResponse(
                        message="✅ Booking confirmed! (Tool not yet configured)",
                        response_type=ResponseType.DIRECT,
                        intent="booking",
                        confidence=1.0
                    )
            else:
                state.end_flow()
                return OrchestratorResponse(
                    message="❌ Booking cancelled. Let me know if you'd like to start over!",
                    response_type=ResponseType.DIRECT,
                    intent="booking",
                    confidence=1.0
                )

        # Collect information step by step
        data = state.flow_data

        if not data.get("vehicle_type"):
            data["vehicle_type"] = message
        elif not data.get("pickup_location"):
            data["pickup_location"] = message
        elif not data.get("dropoff_location"):
            data["dropoff_location"] = message
        elif not data.get("date"):
            data["date"] = message
        elif not data.get("time"):
            data["time"] = message

        # Ask next question or confirm
        next_question = self._get_next_booking_question(data)

        if next_question:
            return OrchestratorResponse(
                message=next_question,
                response_type=ResponseType.MULTI_TURN,
                intent="booking",
                confidence=1.0,
                requires_followup=True,
                metadata={"collected": data}
            )
        else:
            return await self._confirm_booking(state, "booking", 1.0)

    async def _continue_payment_flow(
            self,
            state: ConversationState,
            message: str
    ) -> OrchestratorResponse:
        """Continue payment multi-turn flow"""

        data = state.flow_data

        if not data.get("amount"):
            data["amount"] = message
            return OrchestratorResponse(
                message="👤 Who would you like to send money to?",
                response_type=ResponseType.MULTI_TURN,
                intent="payment",
                confidence=1.0,
                requires_followup=True
            )
        elif not data.get("recipient"):
            data["recipient"] = message
            return OrchestratorResponse(
                message="💳 Which payment method? (M-Pesa, credit card, bank transfer)",
                response_type=ResponseType.MULTI_TURN,
                intent="payment",
                confidence=1.0,
                requires_followup=True
            )
        elif not data.get("method"):
            data["method"] = message
            state.end_flow()

            return OrchestratorResponse(
                message=f"✅ Payment of {data['amount']} to {data['recipient']} via {data['method']} initiated!",
                response_type=ResponseType.DIRECT,
                intent="payment",
                confidence=1.0,
                metadata={"payment_completed": True, "details": data}
            )

        state.end_flow()
        return OrchestratorResponse(
            message="✅ Payment flow completed!",
            response_type=ResponseType.DIRECT,
            intent="payment",
            confidence=1.0
        )

    def _error_response(self, intent: str, confidence: float) -> OrchestratorResponse:
        """Generate error response"""
        return OrchestratorResponse(
            message="❌ I encountered an error processing your request. Please try again.",
            response_type=ResponseType.DIRECT,
            intent=intent,
            confidence=confidence,
            metadata={"error": True}
        )