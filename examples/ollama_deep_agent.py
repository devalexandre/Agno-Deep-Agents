import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agno_deep_agents import create_deep_agent


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


agent = create_deep_agent(
    model="ollama:gemma4:e4b",
    tools=[get_weather],
    instructions="You are a helpful assistant. Prefer concise, practical answers.",
)


if __name__ == "__main__":
    agent.print_response("What is the weather in sf?", stream=True)
