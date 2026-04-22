---
title: Python API
---

# Python API

The public API is intentionally small.

## `create_deep_agent`

Use it when you want direct control over the agent:

```python
from agno_deep_agents import create_deep_agent


agent = create_deep_agent(
    model="ollama:gemma4:e4b",
    instructions="Be practical and answer in English.",
)

agent.print_response("Analyze this project.", stream=True)
```

Common parameters:

| Parameter | Description |
| --- | --- |
| `model` | Provider string or an `agno.models.base.Model` instance. |
| `tools` | Extra Python functions or Agno toolkits. |
| `instructions` | Extra instruction added to the team leader. |
| `workspace` | Root directory for file and shell tools. |
| `db_file` | SQLite path. |
| `skills_dir` | Local skills directory. |
| `ollama_host` | Custom Ollama host. |
| `enable_shell` | Enables or disables `run_shell`. |
| `max_iterations` | Team task-loop limit. |
| `show_members_responses` | Shows or hides specialist member responses. |

## `DeepAgentConfig`

Use it when configuration grows:

```python
from agno_deep_agents import DeepAgentConfig, create_deep_agent


config = DeepAgentConfig(
    workspace=".",
    model="openai-responses:gpt-5.2",
    enable_shell=True,
    max_iterations=8,
)

agent = create_deep_agent(config)
```

## `run_deep_agent`

Use it for direct execution:

```python
from agno_deep_agents import run_deep_agent


run_deep_agent(
    "Map the project and recommend the next useful improvement.",
    user_id="dev@example.com",
    session_id="demo",
)
```

## Custom Tools

Python functions can be passed through `tools`, following the Agno pattern:

```python
from agno_deep_agents import create_deep_agent


def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"It's always sunny in {city}!"


agent = create_deep_agent(
    model="ollama:gemma4:e4b",
    tools=[get_weather],
)
```
