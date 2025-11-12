# app/agents/main_agent.py

from langchain.agents import initialize_agent, AgentType
from app.core.agentic_layer.tools.tool_registry import get_registered_tools

async def agentic_router(message, intent, memory):
    """Handles message routing via LangChain agent tools."""

    agent = initialize_agent(
        tools=get_registered_tools,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        memory=memory,
        verbose=True
    )

    response = agent.run(message)
    return response
