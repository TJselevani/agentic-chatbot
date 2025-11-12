# main.py
from app.core.agentic_layer.agents.agent import create_agent

if __name__ == "__main__":
    agent = create_agent()
    response = agent.run("Book a sedan from Nairobi to Kisumu.")
    print(response)
