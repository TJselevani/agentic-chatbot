from app.core.agentic_layer.agent import create_agent
from rag_layer.faq_retriever import FAQRetriever
from intent_layer.intent_classifier import IntentClassifier
from memory_layer.conversation_memory import ConversationManager
from memory_layer.slot_manager import SlotManager
from multilingual_layer.language_detector import LanguageDetector
from multilingual_layer.translator import Translator


class IntentRouter:
    def __init__(self, model_path: str):
        self.classifier = IntentClassifier(model_path)
        self.agent = create_agent()
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
        intent, confidence = self.classifier.predict_intent(translated_message)
        print(f"🎯 Intent: {intent} (confidence: {confidence:.2f})")

        # Route logic (same as before)
        if confidence < 0.6:
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

    def _continue_conversation(self, intent, message):
        # Continue filling slots for active intent
        active = self.active_intent
        missing_slots = self.slots.get_missing_slots(active)

        if not missing_slots:
            # If all slots are filled, execute the action
            response = self._execute_intent(active)
            self.memory.update(message, response)
            self.active_intent = None
            return response

        # Assume user just answered the last question
        slot_to_fill = missing_slots[0]
        self.slots.update_slot(active, slot_to_fill, message)

        remaining = self.slots.get_missing_slots(active)
        if remaining:
            next_slot = remaining[0]
            question = self._ask_for_slot(active, next_slot)
            self.memory.update(message, question)
            return question
        else:
            response = self._execute_intent(active)
            self.memory.update(message, response)
            self.active_intent = None
            return response

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

# from agentic_layer.agent import create_agent
# from rag_layer.faq_retriever import FAQRetriever
# from intent_layer.intent_classifier import IntentClassifier
#
# class IntentRouter:
#     def __init__(self, model_path: str):
#         self.classifier = IntentClassifier(model_path)
#         self.agent = create_agent()
#         self.faq_retriever = FAQRetriever()
#
#     def handle_message(self, message: str):
#         intent, confidence = self.classifier.predict_intent(message)
#         print(f"🎯 Intent: {intent} (confidence: {confidence:.2f})")
#
#         # If confidence is low → fallback or ask clarification
#         if confidence < 0.6:
#             return "🤔 I'm not sure what you mean. Could you rephrase that?"
#
#         # Route based on intent
#         if intent == "faq_query":
#             answer = self.faq_retriever.retrieve_answer(message)
#             return answer
#
#         elif intent in ["book_vehicle", "get_weather", "collect_feedback"]:
#             response = self.agent.run(message)
#             return response
#
#         else:
#             return "⚙️ I'm still learning how to handle that request."
