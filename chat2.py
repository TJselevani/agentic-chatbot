from app.core.intent_layer.intent_router import IntentRouter

if __name__ == "__main__":
    model_path = "./models/intent_model"
    router = IntentRouter(model_path)

    print("🚀 Agentic Chatbot ready!")
    while True:
        user_input = input("\n👤 You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break
        response = router.handle_message(user_input)
        print(f"🤖 Bot: {response}")
