import json
import os
# from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.config import settings

def initialize_vectorstore():
    """Initialize or rebuild vector store from FAQs"""
    faq_path = os.path.join(settings.VECTOR_DB_PATH, "faq_data.json")
    db_path = os.path.join(settings.BASE_DIR, "database", "chroma_db")

    with open(faq_path, "r", encoding="utf-8") as f:
        faq_data = json.load(f)

    texts = [f"Q: {item['question']} A: {item['answer']}" for item in faq_data]
    metadatas = [{"question": item["question"], "answer": item["answer"]} for item in faq_data]

    embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
    vectorstore = Chroma.from_texts(texts, embedding=embeddings, metadatas=metadatas, persist_directory=db_path)
    vectorstore.persist()

    print(f"✅ Vectorstore initialized with {len(faq_data)} FAQs at {db_path}")
    return vectorstore


if __name__ == "__main__":
    initialize_vectorstore()
