import torch
import os
import torch.nn as nn
from typing import Dict, Tuple
from app.config import settings
from utils.nltk_utils import tokenize, bag_of_words


class NeuralNet(nn.Module):
    """Simple feedforward neural network for intent classification."""

    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNet, self).__init__()
        self.l1 = nn.Linear(input_size, hidden_size)
        self.l2 = nn.Linear(hidden_size, hidden_size)
        self.l3 = nn.Linear(hidden_size, num_classes)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)

    def forward(self, x):
        out = self.l1(x)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.l2(out)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.l3(out)
        return out


class IntentClassifierService:
    """
    Updated Intent Classifier:
    - Uses the ORIGINAL PyTorch NeuralNet (feedforward model)
    - Returns the NEW standardized output structure
    """

    CONFIDENCE_THRESHOLD = 0.65  # same as your new classifier

    def __init__(self, model_path: str = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # ---------------------------
        # Load trained original model
        # ---------------------------
        model_path = model_path or os.path.join(settings.MODEL_DIR, "intent_model.pth")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"❌ Intent model not found at {model_path}")

        data = torch.load(model_path, map_location=self.device)

        self.input_size = data["input_size"]
        self.hidden_size = data["hidden_size"]
        self.output_size = data["output_size"]
        self.all_words = data["all_words"]
        self.tags = data["tags"]

        # Build feed-forward neural network (original model)
        self.model = NeuralNet(self.input_size, self.hidden_size, self.output_size).to(self.device)
        self.model.load_state_dict(data["model_state"])
        self.model.eval()

        print(f"✅ Loaded intent model with {len(self.tags)} intents")

    # --------------------------------------------------------
    # Preprocess input text using original tokenization + BOW
    # --------------------------------------------------------
    def preprocess(self, text: str):
        tokens = tokenize(text)
        bow = bag_of_words(tokens, self.all_words)
        bow = bow.reshape(1, bow.shape[0])
        return torch.from_numpy(bow).to(self.device)

    # --------------------------------------------------------
    # Predict intent using original model
    # --------------------------------------------------------
    def predict(self, text: str) -> Tuple[str, float, Dict]:
        X = self.preprocess(text)

        with torch.no_grad():
            output = self.model(X)

            probs = torch.softmax(output, dim=1)
            conf, predicted = torch.max(probs, dim=1)

            intent = self.tags[predicted.item()]
            confidence_score = conf.item()

            # Build probability dict for all intents
            all_probs = {
                self.tags[i]: probs[0][i].item()
                for i in range(len(self.tags))
            }

            return intent, confidence_score, all_probs

    def is_high_confidence(self, conf: float) -> bool:
        return conf >= self.CONFIDENCE_THRESHOLD

    # --------------------------------------------------------
    # The required unified details
    # --------------------------------------------------------
    def get_intent_details(self, text: str) -> Dict:
        intent, confidence, probabilities = self.predict(text)

        return {
            "intent": intent,
            "confidence": confidence,
            "high_confidence": self.is_high_confidence(confidence),
            "all_probabilities": probabilities,
            "needs_llm_verification": not self.is_high_confidence(confidence)
        }


# ---------------------------
# Global Singleton Instance
# ---------------------------
_classifier_instance = None


def get_intent_classifier() -> IntentClassifierService:
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = IntentClassifierService()
    return _classifier_instance


def get_intent(text: str) -> str:
    classifier = get_intent_classifier()
    intent, _, _ = classifier.predict(text)
    return intent


def get_intent_with_confidence(text: str) -> Dict:
    classifier = get_intent_classifier()
    return classifier.get_intent_details(text)
