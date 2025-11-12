# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    MODEL_DIR = os.path.join(BASE_DIR, "models")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    VECTOR_DB_PATH = os.path.join(BASE_DIR, "app/vectorstore/faqs")

settings = Settings()
