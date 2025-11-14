# app/core/intent_layer/intent_classifier.py
import torch
import torch.nn as nn
from typing import Dict, Tuple
import json
import os
from app.config import settings


class IntentClassifier(nn.Module):
    """PyTorch Intent Classification Model"""

    def __init__(self, vocab_size: int, embedding_dim: int = 128, hidden_dim: int = 64, num_classes: int = 5):
        super(IntentClassifier, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, num_classes)
        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        embedded = self.embedding(x)
        lstm_out, (hidden, _) = self.lstm(embedded)
        # Concatenate final forward and backward hidden states
        hidden = torch.cat((hidden[-2], hidden[-1]), dim=1)
        hidden = self.dropout(hidden)
        output = self.fc(hidden)
        return output


class IntentClassifierService:
    """Service for intent classification with confidence scoring"""

    INTENT_LABELS = {
        0: "faq",  # General questions about services
        1: "booking",  # Vehicle booking requests
        2: "payment",  # Payment and money transfer
        3: "weather",  # Weather inquiries
        4: "general",  # General conversation
    }

    CONFIDENCE_THRESHOLD = 0.65  # Threshold for high confidence

    def __init__(self, model_path: str = None, vocab_path: str = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load vocabulary
        vocab_path = vocab_path or os.path.join(settings.BASE_DIR, "data", "vocab.json")
        with open(vocab_path, 'r') as f:
            self.vocab = json.load(f)

        self.word2idx = self.vocab.get("word2idx", {})
        self.idx2word = self.vocab.get("idx2word", {})

        # Initialize model
        vocab_size = len(self.word2idx)
        num_classes = len(self.INTENT_LABELS)
        self.model = IntentClassifier(vocab_size, num_classes=num_classes)

        # Load trained weights if available
        model_path = model_path or os.path.join(settings.BASE_DIR, "models", "intent_model.pt")
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            print(f"✅ Intent model loaded from {model_path}")
        else:
            print(f"⚠️ No trained model found at {model_path}. Using untrained model.")

        self.model.to(self.device)
        self.model.eval()

    def preprocess_text(self, text: str, max_length: int = 50) -> torch.Tensor:
        """Convert text to tensor of token indices"""
        tokens = text.lower().split()
        indices = [self.word2idx.get(token, self.word2idx.get("<UNK>", 1)) for token in tokens]

        # Pad or truncate
        if len(indices) < max_length:
            indices += [0] * (max_length - len(indices))
        else:
            indices = indices[:max_length]

        return torch.tensor([indices], dtype=torch.long).to(self.device)

    def predict(self, text: str) -> Tuple[str, float, Dict]:
        """
        Predict intent with confidence score
        Returns: (intent_label, confidence, probabilities_dict)
        """
        with torch.no_grad():
            input_tensor = self.preprocess_text(text)
            logits = self.model(input_tensor)
            probabilities = torch.softmax(logits, dim=1)
            confidence, predicted_idx = torch.max(probabilities, dim=1)

            intent = self.INTENT_LABELS[predicted_idx.item()]
            confidence_score = confidence.item()

            # Get all probabilities
            all_probs = {
                self.INTENT_LABELS[i]: probabilities[0][i].item()
                for i in range(len(self.INTENT_LABELS))
            }

            return intent, confidence_score, all_probs

    def is_high_confidence(self, confidence: float) -> bool:
        """Check if confidence is above threshold"""
        return confidence >= self.CONFIDENCE_THRESHOLD

    def get_intent_details(self, text: str) -> Dict:
        """
        Get detailed intent classification results
        """
        intent, confidence, probabilities = self.predict(text)

        return {
            "intent": intent,
            "confidence": confidence,
            "high_confidence": self.is_high_confidence(confidence),
            "all_probabilities": probabilities,
            "needs_llm_verification": not self.is_high_confidence(confidence)
        }


# Global instance
_classifier_instance = None


def get_intent_classifier() -> IntentClassifierService:
    """Singleton pattern for intent classifier"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = IntentClassifierService()
    return _classifier_instance


def get_intent(text: str) -> str:
    """Quick intent prediction (for backward compatibility)"""
    classifier = get_intent_classifier()
    intent, _, _ = classifier.predict(text)
    return intent


def get_intent_with_confidence(text: str) -> Dict:
    """Get intent with full details"""
    classifier = get_intent_classifier()
    return classifier.get_intent_details(text)