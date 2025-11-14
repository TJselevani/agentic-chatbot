# main.py
from app.core.agentic_layer.agent_manager import AgentManager


if __name__ == "__main__":
    agent_manager = AgentManager()
    azure = agent_manager.get_agent("azure")
    response = azure.run("Book a sedan from Nairobi to Kisumu.")
    print(response)
