# Agno Deep Agent

An opinionated **Deep Agent** harness built with Agno primitives. The goal is to
give users a simple CLI and Python API while still supporting the building
blocks needed for long-running agentic work: planning, subagents, workspace
tools, optional shell execution, lazy-loaded skills, persistent memory, and
learning.

## Documentation

The GitHub Pages documentation lives in [`docs/`](docs/index.md). To publish it,
configure GitHub Pages with branch `main` and folder `/docs`.

Project planning lives in [ROADMAP.md](ROADMAP.md). Protocol direction for ACP,
MCP, and AgentOS is documented in [`docs/protocols.md`](docs/protocols.md).

## What Is Included

- **`TeamMode.tasks`** to decompose, execute, and review work in a task loop.
- **Specialist subagents**:
  - `Researcher`: inspects the workspace and identifies constraints before edits.
  - `Implementer`: changes files and runs allowed verification commands.
  - `Reviewer`: checks regressions, verification gaps, and clarity.
- **SQLite** at `.deep-agent/agno.db` for sessions, memory, and learning.
- **Local skills** in `skills/`, loaded through Agno progressive discovery.
- **Workspace-restricted `CodingTools`**.
- **Agno context compression** for long tool-heavy sessions.
- **Multimodal input** through Agno media classes for images, audio, video, and files.
- **Installable CLI** with `agno-deep-agent`, plus aliases `agdeep` and `news`.
- **Interactive CLI** with Agno logo/wordmark, Agno-colored status, model switching,
  compression toggles, and media attachments.
- **ACP stdio server** for editor and IDE integration.
- **Protocol roadmap** for MCP tool loading and AgentOS.

> Note: shell execution is restricted by workspace, command allowlist, timeout,
> and `CodingTools` operator checks. This is useful in practice, but it is not an
> operating-system or container sandbox.

## Installation

Install directly from the remote repository, without cloning it first:

```bash
python -m venv .venv
source .venv/bin/activate
pip install "git+https://github.com/devalexandre/Agno-Deep-Agents.git"
```

Install a specific branch, tag, or commit:

```bash
pip install "git+https://github.com/devalexandre/Agno-Deep-Agents.git@main"
```

For local development after cloning the repository:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Then run:

```bash
agno-deep-agent --help
```

Short aliases:

```bash
agdeep --help
news --help
```

Dependency-only install, without registering the CLI command:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you use OpenAI models, set your API key:

```bash
export OPENAI_API_KEY="your-key-here"
```

Optionally set a default model:

```bash
export DEEP_AGENT_MODEL="openai-responses:gpt-5.2"
```

For local Ollama, start Ollama and pull a model. The `ollama:` provider uses
`http://localhost:11434` by default, even when `OLLAMA_API_KEY` is set:

```bash
ollama pull devstral-2
agno-deep-agent --model ollama:devstral-2 "Use a simple tool and answer briefly"
```

If Ollama is running on another host:

```bash
agno-deep-agent --model ollama:devstral-2 --ollama-host http://localhost:11434 \
  "Analyze the project and create a plan"
```

Use Ollama Cloud explicitly with:

```bash
agno-deep-agent --model ollama-cloud:devstral-2 "Answer briefly"
```

## CLI Usage

Start an interactive Agno-colored session:

```bash
agno-deep-agent
```

The interactive CLI opens with an `Agno Deep Agents` ASCII banner, an Agno logo
mark, Agno orange tokens (`#FF4017`, `#C92D11`, `#FF7A45`), and a compact prompt:

```text
▌ >
```

Pass a task directly:

```bash
agno-deep-agent "Analyze this project, fix obvious issues, and update the README"
```

Or pipe the task through stdin:

```bash
printf "Create a CLI for running the agent with persistent memory" | agno-deep-agent
```

Attach multimodal context when the selected model supports it:

```bash
agno-deep-agent --image screenshot.png --file docs/spec.pdf \
  "Review the UI and compare it with the spec"
```

Use compression controls for long sessions:

```bash
agno-deep-agent --compression-model openai-responses:gpt-4o-mini \
  --compression-limit 2 \
  "Analyze this repository and keep context compact"
```

Disable shell execution when you want file tools only:

```bash
agno-deep-agent --no-shell "Review the current architecture and suggest improvements"
```

Continue a session with a stable `session-id`:

```bash
agno-deep-agent --user-id dev@example.com --session-id agno-deep-agent-local \
  "Continue the previous task and validate what remains"
```

Run as an ACP server for compatible editors and IDEs:

```bash
agdeep acp --model ollama:gemma4:e4b --workspace /absolute/path/to/project
```

The ACP server speaks newline-delimited JSON-RPC over stdio. It supports
`initialize`, `session/new`, `session/load`, `session/prompt`, and
`session/cancel`, while reusing the same Agno `Team`, skills, memory, and
workspace tooling as the normal CLI.

## Python API

```python
from agno_deep_agents import DeepAgentConfig, run_deep_agent

config = DeepAgentConfig(
    workspace=".",
    model="openai-responses:gpt-5.2",
    enable_shell=True,
    compress_tool_results=True,
    max_iterations=8,
)

run_deep_agent(
    "Map the project, implement a small improvement, and run the available checks.",
    config,
    user_id="dev@example.com",
    session_id="demo",
)
```

Send multimodal inputs through the SDK:

```python
from agno_deep_agents import DeepAgentConfig, DeepAgentMedia, run_deep_agent


run_deep_agent(
    "Explain the screenshot and suggest one implementation fix.",
    DeepAgentConfig(model="openai-responses:gpt-5.2"),
    media=DeepAgentMedia(images=["screenshot.png"]),
)
```

For an API close to the DeepAgents ergonomics, but using Agno patterns:

```python
from agno_deep_agents import create_deep_agent


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


agent = create_deep_agent(
    model="ollama:devstral-2",
    tools=[get_weather],
    instructions="You are a helpful assistant.",
)

agent.print_response("what is the weather in sf?", stream=True)
```

## Mapping To Deep Agents

- **Planning**: `TeamMode.tasks` and the `deep-agent-planning` skill.
- **Subagents**: clear `Team` members with specialist roles.
- **Filesystem**: `CodingTools` with `base_dir` and `restrict_to_base_dir=True`.
- **Shell**: `CodingTools.run_shell` with command allowlist and timeout.
- **Memory and learning**: `SqliteDb`, `enable_agentic_memory=True`, and `learning=True`.
- **Context engineering**: history, session summaries, memory, lazy-loaded skills,
  and Agno `compress_tool_results`.
- **Multimodal**: Agno `Image`, `Audio`, `Video`, and `File` inputs from the CLI
  and SDK.
- **Model providers**: simple Agno-style model strings such as
  `openai-responses:gpt-5.2`, `openai:gpt-5.2`, `ollama:llama3.1:8b`, and
  `ollama-responses:gpt-oss:20b`. Use `ollama-cloud:<model>` for Ollama Cloud.
- **Protocols**: ACP is available as a stdio server for editor/IDE integration,
  MCP is planned for external tool loading, and AgentOS is planned as an
  Agno-native API example.

## Project Structure

```text
.
+-- agno_deep_agents/
|   +-- __init__.py
|   +-- cli.py
|   +-- deep_agent.py
+-- docs/
|   +-- index.md
|   +-- ...
|   +-- protocols.md
|   +-- roadmap.md
+-- examples/
|   +-- ollama_deep_agent.py
+-- skills/
|   +-- codebase-analysis/
|   |   +-- SKILL.md
|   +-- deep-agent-planning/
|       +-- SKILL.md
+-- main.py
+-- pyproject.toml
+-- README.md
+-- ROADMAP.md
+-- requirements.txt
```
