import json
import os
import openai
from langchain_openai import OpenAIEmbeddings

# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from app.config import settings

api_keys = [settings.OPENAI_API_KEY]
valid_keys = []


def is_valid_key(api_key: str) -> bool:
    """Check if an OpenAI API key is valid by making a test request."""
    try:
        openai.api_key = api_key
        # Lightweight test request
        openai.models.list()
        return True
    except Exception as e:
        print(f"Key {api_key[:10]}... is invalid: {e}")
        return False


def create_embedding():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def get_embeddings():
    """
    Select embeddings provider based on available credentials.
    Priority:
    1. OpenAI API Key
    2. Azure/GitHub token (simulate gpt-4o-mini embeddings)
    3. Local HuggingFace embeddings (offline fallback)
    """
    if settings.OPENAI_API_KEY and is_valid_key(settings.OPENAI_API_KEY):
        print("🔑 Using OpenAI embeddings")
        return OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

    elif os.environ.get("GITHUB_TOKEN"):
        print("🔑 Using Azure/GitHub token with gpt-4o-mini embeddings")
        # NOTE: LangChain doesn’t yet expose embeddings via azure.ai.inference,
        # but you can wrap ChatOpenAI as an embedding generator.
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=settings.GITHUB_KEY,
            base_url="https://models.github.ai/inference",
        )

        # Simple wrapper: use LLM to embed text by asking for vector representation
        # (for testing only, not production-ready)
        class GPT4oMiniEmbeddings:
            def embed_documents(self, docs):
                return [llm.embed_query(doc) for doc in docs]

            def embed_query(self, query):
                return llm.embed_query(query)

        return GPT4oMiniEmbeddings()

    else:
        print("⚡ No API keys found, using HuggingFace embeddings (all-MiniLM-L6-v2)")
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )


def initialize_vectorstore():
    """Initialize or rebuild vector store from FAQs"""
    faq_path = os.path.join(settings.VECTOR_DB_PATH, "faq_data.json")
    db_path = os.path.join(settings.BASE_DIR, "database", "chroma_db")

    with open(faq_path, "r", encoding="utf-8") as f:
        faq_data = json.load(f)

    texts = [f"Q: {item['question']} A: {item['answer']}" for item in faq_data]
    metadatas = [
        {"question": item["question"], "answer": item["answer"]} for item in faq_data
    ]

    embeddings = create_embedding()
    vectorstore = Chroma.from_texts(
        texts, embedding=embeddings, metadatas=metadatas, persist_directory=db_path
    )
    vectorstore.persist()

    print(f"✅ Vectorstore initialized with {len(faq_data)} FAQs at {db_path}")
    return vectorstore


if __name__ == "__main__":
    initialize_vectorstore()
