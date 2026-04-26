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
| `allowed_shell_commands` | Command-name allow-list for shell tools. |
| `allow_all_shell_commands` | Disable command-name filtering while keeping workspace checks. |
| `compress_tool_results` | Enable Agno context compression for tool results. |
| `compression_model` | Optional model used only for compression. |
| `compression_tool_results_limit` | Compress after N uncompressed tool results. |
| `compression_token_limit` | Compress after a token threshold. |
| `send_media_to_model` | Send attached media to the model. |
| `store_media` | Store attached media in Agno session storage. |
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
    compress_tool_results=True,
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

`run_deep_agent` also accepts multimodal input through `DeepAgentMedia` or direct
`images`, `audio`, `videos`, and `files` keyword arguments:

```python
from agno_deep_agents import DeepAgentConfig, DeepAgentMedia, run_deep_agent


run_deep_agent(
    "Describe this screenshot and suggest one UI fix.",
    DeepAgentConfig(model="openai-responses:gpt-5.2"),
    media=DeepAgentMedia(images=["screenshot.png"]),
)
```

Use a dedicated compression model when the main model is expensive:

```python
from agno_deep_agents import DeepAgentConfig, create_deep_agent


agent = create_deep_agent(
    DeepAgentConfig(
        model="openai-responses:gpt-5.2",
        compression_model="openai-responses:gpt-4o-mini",
        compression_tool_results_limit=2,
    )
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
