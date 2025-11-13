import torch
import torch.nn as nn
import torch.nn.functional as F
import os
import numpy as np
from app.config import settings
from utils.nltk_utils import tokenize, bag_of_words


# ==== MODEL DEFINITION (same as training) ====
class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNet, self).__init__()
        self.l1 = nn.Linear(input_size, hidden_size)
        self.l2 = nn.Linear(hidden_size, hidden_size)
        self.l3 = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        x = F.relu(self.l1(x))
        x = F.relu(self.l2(x))
        x = self.l3(x)
        return x


# ==== GLOBALS ====
model = None
all_words = None
all_intents = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ==== LOAD MODEL ====
def load_model():
    global model, all_words, all_intents

    model_path = os.path.join(settings.MODEL_DIR, "intent_model.pth")
    checkpoint = torch.load(model_path, map_location=device)

    input_size = checkpoint["input_size"]
    hidden_size = checkpoint["hidden_size"]
    output_size = checkpoint["output_size"]
    all_words = checkpoint["all_words"]
    all_intents = checkpoint["tags"]

    model = NeuralNet(input_size, hidden_size, output_size).to(device)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    print("✅ Intent model loaded successfully.")


# ==== PREPROCESS USER TEXT ====
def preprocess_text(sentence: str):
    tokens = tokenize(sentence)
    bow = bag_of_words(tokens, all_words)
    bow = np.array(bow, dtype=np.float32)   # ✅ Convert to NumPy first
    return torch.from_numpy(bow).unsqueeze(0)


# ==== GET INTENT ====
def get_intent(user_text: str):
    global model

    if model is None:
        load_model()

    X = preprocess_text(user_text).to(device)
    with torch.no_grad():
        output = model(X)
        probs = torch.softmax(output, dim=1)
        predicted_index = torch.argmax(probs, dim=1).item()
        confidence = probs[0][predicted_index].item()

    intent_label = all_intents[predicted_index]
    print(f"🧩 Detected intent: {intent_label} ({confidence:.2f})")
    return intent_label
