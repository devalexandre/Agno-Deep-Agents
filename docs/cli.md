---
title: CLI
---

# CLI

The `agno-deep-agent` command provides a simple interface for running the
harness. The short alias `agdeep` points to the same CLI.

## Install The CLI

Install directly from the remote repository:

```bash
pip install "git+https://github.com/devalexandre/Agno-Deep-Agents.git"
```

For local development after cloning:

```bash
pip install -e .
```

Then:

```bash
agno-deep-agent --help
```

`python main.py` still works as a development compatibility wrapper.

## Basic Usage

```bash
agno-deep-agent "Analyze this project and suggest one small improvement"
```

You can also pass the task through `stdin`:

```bash
printf "Review the documentation and find gaps" | agno-deep-agent
```

## Main Options

| Option | Description |
| --- | --- |
| `--model` | Model string in `provider:model` format. |
| `--workspace` | Workspace root for filesystem and shell tools. |
| `--db-file` | SQLite path for sessions, memory, and learning. |
| `--skills-dir` | Directory containing local skills. |
| `--ollama-host` | Custom Ollama host. |
| `--user-id` | Stable user identifier for memory. |
| `--session-id` | Stable session identifier for continuing work. |
| `--max-iterations` | Maximum team task-loop iterations. |
| `--no-shell` | Disable shell execution. |
| `--no-stream` | Print the answer only after completion. |
| `--hide-members` | Hide specialist member responses. |
| `--debug` | Enable Agno debug mode. |

## ACP Server

Run Agno Deep Agent as an ACP stdio server:

```bash
agdeep acp --model ollama:gemma4:e4b --workspace /absolute/path/to/project
```

ACP clients launch this command as a subprocess and communicate through
newline-delimited JSON-RPC. The server writes protocol messages to stdout and
uses stderr for logs.

Supported ACP methods:

| Method | Status |
| --- | --- |
| `initialize` | Supported |
| `session/new` | Supported |
| `session/load` | Supported |
| `session/prompt` | Supported |
| `session/cancel` | Supported |

For per-editor ACP setup notes (Zed, VS Code-compatible extensions, JetBrains,
and Neovim), see [ACP Editors](acp-editors.html).

## Examples

Run with local Ollama:

```bash
agno-deep-agent --model ollama:gemma4:e4b \
  "List the main files and explain each role"
```

Run without shell:

```bash
agno-deep-agent --no-shell \
  "Read the README and propose a clearer structure"
```

Continue a session:

```bash
agno-deep-agent --user-id dev@example.com --session-id local-docs \
  "Continue the last task and summarize what remains"
```

Use a specific workspace:

```bash
agno-deep-agent --workspace /path/to/project \
  "Analyze the project and find implementation risks"
```
