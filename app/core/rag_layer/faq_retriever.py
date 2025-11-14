from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.vectorstore.initialize_store import create_embedding


class FAQRetriever:
    def __init__(self):
        # Dummy in-memory store (replace with FAISS + real data)
        docs = [
            Document(page_content="To book a vehicle, simply provide your pickup and dropoff locations."),
            Document(page_content="You can cancel a booking from your dashboard anytime."),
            Document(page_content="Payments can be made using M-Pesa, credit card, or cash.")
        ]
        self.embeddings = create_embedding()
        self.store = FAISS.from_documents(docs, self.embeddings)

    def retrieve_answer(self, query: str):
        results = self.store.similarity_search(query, k=1)
        if results:
            return results[0].page_content
        return "❓ Sorry, I couldn’t find an answer to that question."
