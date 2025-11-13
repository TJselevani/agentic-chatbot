from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma

from app.config import settings



import os

# ===== Initialize the RAG pipeline =====
def get_vectorstore():
    db_path = os.path.join(settings.VECTOR_DB_PATH, "chroma_db")
    embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
    vectorstore = Chroma(persist_directory=db_path, embedding_function=embeddings)
    return vectorstore


def get_rag_chain():
    """Set up the Retrieval-Augmented Generation chain"""
    llm = ChatOpenAI(model_name="gpt-4-turbo", temperature=0.3, openai_api_key=settings.OPENAI_API_KEY)
    vectorstore = get_vectorstore()

    prompt_template = """Use the following FAQs and context to answer the user's question as accurately as possible.
If the answer isn't directly found, say you don't have that information.

Context:
{context}

Question: {question}
Answer:"""

    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": PROMPT}
    )
    return qa_chain


def handle_faq(query: str):
    """Fetch relevant FAQ info and generate an answer"""
    qa_chain = get_rag_chain()
    result = qa_chain.run(query)
    return result
