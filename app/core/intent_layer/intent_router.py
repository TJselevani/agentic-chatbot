from app.core.intent_layer.intent_classifier import IntentClassifierService
from app.core.memory_layer.conversation_memory import ConversationManager
from app.core.memory_layer.slot_manager import SlotManager
from app.core.multilingual_layer.language_detector import LanguageDetector
from app.core.multilingual_layer.translator import Translator
from app.core.rag_layer.faq_retriever import FAQRetriever
from app.core.agentic_layer.agent_manager import AgentManager

agent_manager = AgentManager()

azure = agent_manager.get_agent("azure")


class IntentRouter:
    def __init__(self, model_path: str = None):
        self.classifier = IntentClassifierService(model_path)
        self.agent = azure
        self.faq_retriever = FAQRetriever()
        self.memory = ConversationManager()
        self.slots = SlotManager()
        self.detector = LanguageDetector()
        self.translator = Translator()

        self.active_intent = None

    def handle_message(self, message: str):
        # Detect language
        lang = self.detector.detect_language(message)
        print(f"🌐 Detected language: {lang}")

        # Translate to English for processing
        translated_message = self.translator.translate_to_english(message, lang)

        # Classify intent on English text
        intent_details = self.classifier.get_intent_details(translated_message)
        intent = intent_details["intent"]
        confidence = intent_details["confidence"]
        high_conf = intent_details["high_confidence"]

        print(f"🎯 Intent: {intent} (confidence: {confidence:.2f}, high_confidence={high_conf})")

        # Route logic
        if not high_conf:
            reply = "🤔 I’m not sure what you mean. Could you rephrase that?"
        elif intent == "faq_query":
            reply = self.faq_retriever.retrieve_answer(translated_message)
        elif intent in ["book_vehicle", "get_weather", "collect_feedback"]:
            self.active_intent = intent
            reply = self._handle_action_intent(intent, translated_message)
        else:
            reply = "⚙️ I’m still learning how to handle that request."

        # Translate back to user’s original language
        final_reply = self.translator.translate_from_english(reply, lang)
        self.memory.update(message, final_reply)
        return final_reply

    def _handle_action_intent(self, intent, message):
        missing_slots = self.slots.get_missing_slots(intent)
        if missing_slots:
            next_slot = missing_slots[0]
            return self._ask_for_slot(intent, next_slot)
        else:
            return self._execute_intent(intent)

    def _ask_for_slot(self, intent, slot_name):
        slot_questions = {
            "pickup": "Where should I pick you up?",
            "dropoff": "Where are you going?",
            "vehicle_type": "What type of vehicle would you like (e.g., sedan, SUV, van)?"
        }
        return slot_questions.get(slot_name, f"Please provide {slot_name}.")

    def _execute_intent(self, intent):
        filled_slots = self.slots.get_filled_slots(intent)
        print(f"✅ All slots collected: {filled_slots}")
        if intent == "book_vehicle":
            return self.agent.run(
                f"Book a {filled_slots.get('vehicle_type')} from {filled_slots.get('pickup')} to {filled_slots.get('dropoff')}."
            )
        elif intent == "get_weather":
            return self.agent.run(f"Get weather for {filled_slots.get('location')}")
        else:
            return "✅ Task completed."
