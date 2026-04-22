---
title: Agno Deep Agent
---

# Agno Deep Agent

Agno Deep Agent is an opinionated harness for building deep agents with the
Agno feel: easy to call, modular inside, and ready for long-running work.

It combines `Team`, `Agent`, `Skills`, `SqliteDb`, memory, learning, and
workspace tools behind a small interface:

```python
from agno_deep_agents import create_deep_agent


agent = create_deep_agent(
    model="ollama:gemma4:e4b",
    instructions="Answer in a practical and concise way.",
)

agent.print_response("Analyze this project and propose the next step.", stream=True)
```

## Goal

The project follows the Deep Agents idea: planning, subagents, filesystem,
shell, memory, and persistent context. The difference is that the implementation
uses Agno primitives instead of introducing a separate runtime.

## Navigation

- [Get Started](getting-started.html)
- [CLI](cli.html)
- [ACP Editors](acp-editors.html)
- [Python API](python-api.html)
- [Models and Ollama](models.html)
- [Architecture](architecture.html)
- [Protocols](protocols.html)
- [Skills](skills.html)
- [Roadmap](roadmap.html)
- [Publish on GitHub Pages](github-pages.html)
- [Troubleshooting](troubleshooting.html)

## What Is Included

- `TeamMode.tasks` to coordinate discovery, implementation, and review.
- Specialist subagents: `Researcher`, `Implementer`, and `Reviewer`.
- SQLite at `.deep-agent/agno.db` for sessions, memory, and learning.
- Local skills in `skills/`.
- Workspace-restricted `CodingTools`.
- Support for OpenAI, local Ollama, and Ollama Cloud through model strings.
- Agno-inspired documentation styling with dark mode and syntax highlighting.
- ACP stdio server plus protocol direction for MCP and AgentOS.

## Custom Tool Example

```python
from agno_deep_agents import create_deep_agent


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


agent = create_deep_agent(
    model="ollama:gemma4:e4b",
    tools=[get_weather],
    instructions="You are a concise assistant.",
)

agent.print_response("What is the weather in sf?", stream=True)
```

## Sandbox Note

Shell execution is restricted by workspace, command allowlist, timeout, and
`CodingTools` operator checks. This reduces operational risk, but it is not the
same as an operating-system or container sandbox.
