# 🤖 Agentic Chatbot System

A next-generation chatbot that combines PyTorch intent classification, AI agents, RAG (Retrieval-Augmented Generation), tool execution, and multi-turn conversations.

## 🌟 Features

- **🎯 Intent Classification**: PyTorch-based model with confidence scoring
- **🤖 AI Agent Integration**: Azure/GitHub Models API for complex reasoning
- **📚 RAG System**: ChromaDB vector store for FAQ retrieval
- **🔧 Tool Execution**: Extensible tool system for external API calls
- **💬 Multi-turn Conversations**: Stateful conversation flows with validation
- **📊 Feedback Collection**: User satisfaction tracking and analytics
- **🌍 Multilingual Support**: Ready for Swahili/Sheng integration

## 📋 Use Cases

1. **FAQ Answering**: Combines PyTorch responses with RAG retrieval
2. **Vehicle Booking**: Multi-step conversation with validation
3. **Payment Processing**: Guided money transfer flows
4. **Weather Queries**: External API tool integration
5. **General Conversation**: AI agent-powered responses

## 🏗️ Architecture

```
User Message
     ↓
Intent Classifier (PyTorch)
     ↓
[High Confidence?] → Yes → Direct Handling
     ↓ No
AI Agent Verification
     ↓
Orchestrator Routes To:
     ├─ FAQ Handler (RAG)
     ├─ Tool Handler (External APIs)
     ├─ Multi-turn Flow (Booking/Payment)
     └─ General Handler (AI Agent)
     ↓
Response + State Update
```

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.9+
python --version

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file:

```env
# Azure/GitHub Models API (Primary)
GITHUB_TOKEN=your_github_token_here

# OpenAI (Optional - for embeddings)
OPENAI_API_KEY=your_openai_key_here

# Redis (Optional - for distributed state)
REDIS_URL=redis://localhost:6379

# Paths
BASE_DIR=.
VECTOR_DB_PATH=./database
```

### Initialize Vector Store

```bash
# Create FAQ data file
mkdir -p database
cat > database/faq_data.json << EOF
[
  {
    "question": "How do I book a vehicle?",
    "answer": "To book a vehicle, simply tell me your pickup location, destination, and preferred time. I'll guide you through the process."
  },
  {
    "question": "What payment methods do you accept?",
    "answer": "We accept M-Pesa, credit cards, debit cards, and bank transfers."
  },
  {
    "question": "Can I cancel my booking?",
    "answer": "Yes, you can cancel your booking anytime from your dashboard or by contacting support."
  }
]
EOF

# Initialize vector store
python -m app.vectorstore.initialize_store
```

### Create Model Files

```bash
# Create model directory
mkdir -p models

# Copy vocab.json (from artifacts)
# Copy or create intent_model.pt (trained PyTorch model)
```

### Training Your Intent Classifier

Here's a simple training script:

```python
# train_intent_model.py
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from app.core.intent_layer.intent_classifier import IntentClassifier
import json

# Sample training data
training_data = [
    ("I want to book a car", 1),  # booking
    ("How much does it cost?", 0),  # faq
    ("Send money to John", 2),  # payment
    ("What's the weather like?", 3),  # weather
    ("Hello, how are you?", 4),  # general
    # Add more examples...
]

# Train your model
# ... (implement training loop)

# Save model
torch.save(model.state_dict(), "models/intent_model.pt")
```

## 🎮 Usage

### Option 1: CLI Chat Interface

```bash
python chat.py
```

Interactive commands:
- Type message to chat
- `history` - View conversation
- `feedback` - Give feedback
- `clear` - New session
- `quit` - Exit

### Option 2: FastAPI Server

```bash
# Start server
uvicorn app.main:app --reload --port 8000

# Open browser
# http://localhost:8000/docs
```

### Option 3: API Requests

```bash
# Chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "I want to book a vehicle",
    "session_id": "session_abc"
  }'

# Submit feedback
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "session_id": "session_abc",
    "rating": 5,
    "sentiment": "positive",
    "comment": "Very helpful!"
  }'

# Get conversation history
curl http://localhost:8000/session/user123/session_abc
```

## 📖 Example Conversations

### Example 1: FAQ with RAG

```
User: How do I book a vehicle?
Bot: [Uses RAG] To book a vehicle, simply tell me your pickup location...

User: What payment methods are available?
Bot: [Uses RAG] We accept M-Pesa, credit cards, debit cards...
```

### Example 2: Vehicle Booking (Multi-turn)

```
User: I need to book a car
Bot: 🚗 What type of vehicle would you like to book?

User: SUV
Bot: 📍 Where should we pick you up?

User: Westlands, Nairobi
Bot: 📍 Where would you like to go?

User: JKIA Airport
Bot: 📅 What date do you need the vehicle?

User: Tomorrow
Bot: 🕐 What time should we pick you up?

User: 3pm
Bot: 📋 **Booking Summary**
     🚗 Vehicle: SUV
     📍 Pickup: Westlands, Nairobi
     📍 Dropoff: JKIA Airport
     📅 Date: Tomorrow
     🕐 Time: 3pm
     
     Would you like to confirm? (yes/no)

User: yes
Bot: ✅ **Booking Confirmed!**
     📋 Booking ID: BK12AB34CD
     💰 Estimated Cost: $75.00
     ...
```

### Example 3: Low Confidence Intent

```
User: I wanna get a ride maybe
Bot: [Low confidence → asks AI agent]
     [Agent verifies: booking intent]
     🚗 I can help you book a ride! What type of vehicle?
```

### Example 4: Weather Query (Tool Usage)

```
User: What's the weather in Nairobi?
Bot: [Extracts city, calls weather tool]
     🌤️ The weather in Nairobi is partly cloudy with 22°C.
```

## 🔧 Adding New Tools

Create a new tool in `app/core/agentic_layer/tools/`:

```python
# my_custom_tool.py
from app.core.agentic_layer.tools.base_tool import ReusableTool

class MyCustomTool(ReusableTool):
    name: str = "my_tool"
    description: str = "Does something useful"
    
    def _run(self, param1: str, param2: int) -> str:
        # Your logic here
        result = f"Processed {param1} with {param2}"
        return result
```

The tool will be auto-discovered and registered!

## 🎯 Intent Handler Customization

Add new intent in `orchestrator.py`:

```python
self.intent_handlers = {
    "faq": self._handle_faq,
    "booking": self._handle_booking,
    "payment": self._handle_payment,
    "weather": self._handle_weather,
    "general": self._handle_general,
    "my_new_intent": self._handle_my_new_intent,  # Add here
}

async def _handle_my_new_intent(self, state, message, intent, confidence):
    # Your handler logic
    pass
```

## 📊 Monitoring & Analytics

```python
# Get feedback statistics
from app.core.agentic_layer.tools.feedback_tool import FeedbackTool

tool = FeedbackTool()
stats = tool.get_feedback_stats()

print(stats)
# {
#   "total": 150,
#   "average_rating": 4.2,
#   "rating_distribution": {1: 5, 2: 8, 3: 20, 4: 45, 5: 72},
#   "sentiment_distribution": {"positive": 120, "neutral": 20, "negative": 10}
# }
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Test specific component
pytest tests/test_orchestrator.py -v

# Test with coverage
pytest --cov=app tests/
```

## 🌍 Multilingual Support

To add Swahili/Sheng support:

1. **Update Intent Classifier**: Train on Swahili/Sheng data
2. **Add Translation Layer**: Use NLLB or MarianMT
3. **Update Embeddings**: Use multilingual model (LaBSE)

```python
# Example translation integration
from transformers import pipeline

translator = pipeline("translation", model="facebook/nllb-200-distilled-600M")

def translate_to_english(text, source_lang="swh_Latn"):
    result = translator(text, src_lang=source_lang, tgt_lang="eng_Latn")
    return result[0]['translation_text']
```

## 🔒 Security Considerations

- ✅ Validate all user inputs
- ✅ Sanitize data before API calls
- ✅ Use environment variables for secrets
- ✅ Implement rate limiting
- ✅ Add authentication for production
- ✅ Encrypt sensitive data in Redis

## 📈 Performance Optimization

1. **Cache Agent Responses**: Use Redis for common queries
2. **Batch Vector Searches**: Group similar queries
3. **Async Tool Execution**: Run tools concurrently
4. **Model Optimization**: Quantize PyTorch model

## 🐛 Troubleshooting

### Issue: "Agent verification failed"
**Solution**: Check GITHUB_TOKEN is valid

### Issue: "Vector store not found"
**Solution**: Run `python -m app.vectorstore.initialize_store`

### Issue: "Low intent confidence"
**Solution**: Add more training data to PyTorch model

### Issue: "Redis connection failed"
**Solution**: Falls back to in-memory storage automatically

## 📦 Deployment

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chatbot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chatbot
  template:
    metadata:
      labels:
        app: chatbot
    spec:
      containers:
      - name: chatbot
        image: your-registry/chatbot:latest
        ports:
        - containerPort: 8000
        env:
        - name: GITHUB_TOKEN
          valueFrom:
            secretKeyRef:
              name: chatbot-secrets
              key: github-token
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

MIT License - feel free to use in your projects!

## 🙏 Acknowledgments

- LangChain for RAG framework
- Anthropic Claude for agent capabilities
- ChromaDB for vector storage
- FastAPI for API framework

## 📞 Support

For questions or issues:
- Open GitHub issue
- Email: support@example.com
- Docs: https://docs.example.com

---

**Built with ❤️ for next-generation conversational AI**