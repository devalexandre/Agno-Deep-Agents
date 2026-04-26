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

Launch an interactive session:

```bash
agno-deep-agent
```

In a wide terminal, the interactive session opens with an Agno-styled banner:

```text
█  ███████████████         █████   ██████  ███    ██  ██████
█  ██           ██        ██   ██ ██       ████   ██ ██    ██
█  ██    ███    ██        ███████ ██   ███ ██ ██  ██ ██    ██
█  ██   █████   ██        ██   ██ ██    ██ ██  ██ ██ ██    ██
█  ██  ███ ███  ██        ██   ██  ██████  ██   ████  ██████
█  ██  ███████  ██
█  ██ ███   ███ ██
█  ███████████████
 ██████  ███████ ███████ ██████      █████   ██████  ███████ ███    ██ ████████ ███████
 ██   ██ ██      ██      ██   ██    ██   ██ ██       ██      ████   ██    ██    ██
 ██   ██ █████   █████   ██████     ███████ ██   ███ █████   ██ ██  ██    ██    ███████
 ██   ██ ██      ██      ██         ██   ██ ██    ██ ██      ██  ██ ██    ██         ██
 ██████  ███████ ███████ ██         ██   ██  ██████  ███████ ██   ████    ██    ███████
                                                                            v0.1.0
model=openai-responses:gpt-5.2 session=cli-... compression=on
Ready to build. What would you like to build?
Enter send • Ctrl+J newline • @ files • / commands
▌ >
```

```bash
agno-deep-agent "Analyze this project and suggest one small improvement"
```

You can also pass the task through `stdin`:

```bash
printf "Review the documentation and find gaps" | agno-deep-agent
```

When stdin is piped and a prompt is also provided, the CLI combines them with
the piped content first. This is useful for reviewing diffs:

```bash
git diff | agno-deep-agent --prompt "Review these changes"
```

## Main Options

Long options remain stable. The CLI also supports short/alias forms for convenience:

| Option (aliases) | Description |
| --- | --- |
| `--model` / `-m` | Model string in `provider:model` format. |
| `--workspace` / `-w` / `--workdir` | Workspace root for filesystem and shell tools. |
| `--db-file` / `--db` | SQLite path for sessions, memory, and learning. |
| `--skills-dir` / `--skills` | Directory containing local skills. |
| `--ollama-host` / `--ollama-url` | Custom Ollama host. |
| `--user-id` / `-u` / `--user` | Stable user identifier for memory. |
| `--session-id` / `-s` / `--session` | Stable session identifier for continuing work. |
| `--max-iterations` / `-n` / `--max-iter` / `--max-turns` | Maximum team task-loop iterations. |
| `--no-shell` / `--no-exec` | Disable shell execution. |
| `--shell-allow-list` / `-S` | Use a command allow-list, `recommended`, or `all`. |
| `--no-compression` | Disable Agno tool-result compression. |
| `--compression-model` | Use a cheaper/faster model for compression. |
| `--compression-limit` | Compress after N uncompressed tool results. |
| `--compression-token-limit` | Compress after a model-counted token threshold. |
| `--image`, `--audio`, `--video`, `--file` | Attach multimodal inputs. |
| `--startup-cmd` | Run a command before the first prompt; output is not injected. |
| `--non-interactive` | Require args/stdin instead of opening the interactive CLI. |
| `--no-stream` / `--quiet-stream` | Print the answer only after completion. |
| `--quiet` / `-q` | Clean output for piping; hides members and buffers the answer. |
| `--hide-members` / `--hide-agents` | Hide specialist member responses. |
| `--debug` / `-d` | Enable Agno debug mode. |

## Visual Identity

The interactive CLI uses the same core Agno tokens as the documentation:

| Token | Hex | Used For |
| --- | --- | --- |
| Agno primary | `#FF4017` | Logo, wordmark, prompt bar, command headings. |
| Agno primary dark | `#C92D11` | Inline labels such as `model`, `session`, and `compression`. |
| Agno accent | `#FF7A45` | Ready state, version, attachment/status highlights. |
| Agno dark background | `#111113` | Recommended terminal background. |
| Agno muted text | `#A1A1AA` | Hints and prompt separators. |

Use `--no-color` or set `NO_COLOR=1` when plain output is preferred.

## Interactive Commands

Inside the interactive CLI:

| Command | Description |
| --- | --- |
| `/status` | Show model, workspace, session, compression, shell, and media state. |
| `/model [provider:model]` | Show or switch the active model. |
| `/compress on\|off\|status` | Toggle Agno tool-result compression. |
| `/attach image <path-or-url>` | Attach an image to the next prompt. |
| `/attach audio <path-or-url>` | Attach audio to the next prompt. |
| `/attach video <path-or-url>` | Attach video to the next prompt. |
| `/attach file <path-or-url>` | Attach a file/document to the next prompt. |
| `/media` | Show pending attachments. |
| `/clear` | Start a fresh session id. |
| `!<command>` | Ask the agent to run an allowed shell command. |
| `/quit` | Exit. |

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

Attach media:

```bash
agno-deep-agent --image ./screenshot.png --file ./docs/spec.pdf \
  "Compare the implementation with these inputs"
```

Use Agno compression with a dedicated compression model:

```bash
agno-deep-agent --compression-model openai-responses:gpt-4o-mini \
  --compression-limit 2 \
  "Do a deep codebase analysis"
```
