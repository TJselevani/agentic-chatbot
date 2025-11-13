import os
from langchain_openai import ChatOpenAI
from langchain.agents import tool, create_react_agent, AgentExecutor

from app.core.agentic_layer.agent_registry import register_agent
from app.core.agentic_layer.agents.base_agent import BaseAgent
from app.core.agentic_layer.tool_registry import get_registered_tools


@register_agent("gpt_4o_mini")
class GPT4oMiniAgent(BaseAgent):
    def __init__(self, memory=None):
        super().__init__(name="gpt_4o_mini", model="gpt-4o-mini", memory=memory)

        tools = get_registered_tools()
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

        # Create a ReAct agent
        react_agent = create_react_agent(llm, tools)

        # Wrap in AgentExecutor
        self.agent = AgentExecutor(agent=react_agent, tools=tools, verbose=True)

    def run(self, message: str):
        return self.agent.invoke({"input": message})

    def run(self, message: str):
        """Run the agent with a user message"""
        return self.agent.run(message)
