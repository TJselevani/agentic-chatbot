# app/core/intent_classifier.py

import torch
import torch.nn.functional as F
import pickle
import os
from app.config import settings  # We'll define this for env paths


# Example model structure (must match the one you trained)
class IntentClassifier(torch.nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(IntentClassifier, self).__init__()
        self.fc1 = torch.nn.Linear(input_size, hidden_size)
        self.fc2 = torch.nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


# ======== LOAD MODEL ONCE AT STARTUP ========
model = None
tokenizer = None
all_intents = None


def load_model():
    """Load model and tokenizer once on startup"""
    global model, tokenizer, all_intents

    model_path = os.path.join(settings.MODEL_DIR, "intent_model.pth")
    tokenizer_path = os.path.join(settings.MODEL_DIR, "tokenizer.pkl")
    intents_path = os.path.join(settings.MODEL_DIR, "intents.pkl")

    # Load label list and tokenizer
    with open(tokenizer_path, "rb") as f:
        tokenizer = pickle.load(f)
    with open(intents_path, "rb") as f:
        all_intents = pickle.load(f)

    input_size = len(tokenizer.word_index)
    hidden_size = 64
    num_classes = len(all_intents)

    model = IntentClassifier(input_size, hidden_size, num_classes)
    model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
    model.eval()

    print("✅ Intent model loaded successfully.")


def preprocess_text(text):
    """Tokenize or vectorize user input"""
    # Example: Bag-of-words
    bow = [0] * len(tokenizer.word_index)
    for word in text.lower().split():
        if word in tokenizer.word_index:
            bow[tokenizer.word_index[word]] = 1
    return torch.tensor([bow], dtype=torch.float32)


def get_intent(user_text: str) -> str:
    """Predict intent from user input"""
    if model is None:
        load_model()

    X = preprocess_text(user_text)
    with torch.no_grad():
        output = model(X)
        probs = torch.softmax(output, dim=1)
        predicted_index = torch.argmax(probs, dim=1).item()
        confidence = probs[0][predicted_index].item()

    intent_label = all_intents[predicted_index]
    print(f"🧩 Detected intent: {intent_label} ({confidence:.2f})")

    return intent_label
