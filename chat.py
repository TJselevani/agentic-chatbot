# main.py
from app.core.agentic_layer.agent_manager import AgentManager

if __name__ == "__main__":
    manager = AgentManager()
    response = manager.run("Book a sedan from Nairobi to Kisumu.")
    print(response)
