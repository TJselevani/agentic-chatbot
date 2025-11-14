import os
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_chroma import Chroma
from app.config import settings
from app.vectorstore.initialize_store import create_embedding


class RagEngine:
    """
    RAG Engine that can work with ANY LLM object.
    (AzureAgent, OpenAIAgent, LocalAgent, etc.)
    """

    def __init__(self, llm):
        self.llm = llm

        # Cached components
        self._vectorstore = None
        self._chain = None

    # ----------------------------------------
    # Load Vectorstore
    # ----------------------------------------
    def load_vectorstore(self):
        if self._vectorstore:
            return self._vectorstore

        # db_path = os.path.join(settings.VECTOR_DB_PATH, "chroma_db")
        db_path = os.path.join(settings.BASE_DIR, "database", "chroma_db")
        embeddings = create_embedding()

        self._vectorstore = Chroma(
            persist_directory=db_path,
            embedding_function=embeddings,
        )
        return self._vectorstore

    # ----------------------------------------
    # Build RAG Chain using injected LLM
    # ----------------------------------------
    def get_chain(self):
        if self._chain:
            return self._chain

        vectorstore = self.load_vectorstore()

        prompt_template = """
Use the following context to answer the user's question.
If the answer isn't in the documents, say: "I don't have that information."

Context:
{context}

Question:
{question}

Answer:
"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"],
        )

        self._chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": PROMPT},
        )

        return self._chain

    # ----------------------------------------
    # Run Query
    # ----------------------------------------
    def run(self, message: str):
        chain = self.get_chain()
        result = chain.invoke({"query": message})
        return result["result"]  # Return only the answer text
