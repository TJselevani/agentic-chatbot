from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain_openai import ChatOpenAI
from app.core.agentic_layer.tools.tool_registry import get_registered_tools

def create_agent(memory):
    tools = get_registered_tools()
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

    agent = initialize_agent(
        tools,
        llm,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
    )
    return agent
