import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F


class IntentClassifier:
    def __init__(self, model_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.intents = ["book_vehicle", "get_weather", "faq_query", "collect_feedback"]

    def predict_intent(self, text: str):
        inputs = self.tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = F.softmax(outputs.logits, dim=-1)
            intent_idx = torch.argmax(probs, dim=-1).item()
            confidence = probs[0][intent_idx].item()
        return self.intents[intent_idx], confidence
