from app.core.agentic_layer.agent_manager import AgentManager
from app.core.agentic_layer.agents.rag_agent import RagAgent

agent_manager = AgentManager()

azure = agent_manager.get_agent("azure")
rag = RagAgent(llm_agent=azure)

print(rag.run("Can I cancel my booking?"))
