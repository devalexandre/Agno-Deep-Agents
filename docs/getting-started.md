---
title: Get Started
---

# Get Started

This guide gets Agno Deep Agent running locally.

## Requirements

- Python 3.11 or newer.
- A model available through any Agno-supported provider.
- `pip` and permission to install dependencies.

## Install The CLI

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

This registers two commands:

```bash
agno-deep-agent --help
agdeep --help
```

If you only want dependencies without registering a command:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## OpenAI

Set your API key:

```bash
export OPENAI_API_KEY="your-key-here"
```

Run:

```bash
agno-deep-agent --model openai-responses:gpt-5.2 \
  "Explain this project's architecture in 5 bullets"
```

## Local Ollama

Start Ollama and confirm the model is available locally:

```bash
ollama list
```

Then run:

```bash
agno-deep-agent --model ollama:gemma4:e4b \
  "Explain this project's architecture in 5 bullets"
```

The `ollama:` provider uses `http://localhost:11434` by default. This prevents
an `OLLAMA_API_KEY` variable from accidentally sending local runs to cloud.

## Other Agno Providers

Use the same Agno `provider:model` strings for Anthropic, Google, Groq, Mistral,
DeepSeek, OpenRouter, Together, LiteLLM, and other supported providers:

```bash
export ANTHROPIC_API_KEY="your-key-here"
agno-deep-agent --model anthropic:claude-sonnet-4-5 \
  "Explain this project's architecture in 5 bullets"
```

In the interactive CLI, run `/models` to see common examples, then switch with
`/model <provider:model>`.

## Interactive CLI

Run without a prompt to open the Agno-colored interactive CLI:

```bash
agno-deep-agent --model ollama:gemma4:e4b
```

The session starts with the `Agno Deep Agents` ASCII banner, an Agno logo mark,
and the prompt:

```text
▌ >
```

The CLI uses Agno's orange palette (`#FF4017`, `#C92D11`, `#FF7A45`) on a dark
terminal background. Pass `--no-color` if your terminal or logs need plain text.

Useful commands inside the session:

```text
/status
/models
/model openai-responses:gpt-5.2
/compress status
/attach image screenshot.png
/quit
```

The same commands have short aliases, for example `/s`, `/p`, `/m`, `/c`, `/a`,
`/ma`, `/cl`, `/h`, and `/q`.

When you switch with `/model ...`, Agno Deep Agent saves the model in
`.deep-agent/config.json` for the current workspace and reuses it on the next
run. Use `--model ...` when you want a one-off override.

## Multimodal And Compression

Attach media when your model supports the modality:

```bash
agno-deep-agent --image screenshot.png --file docs/spec.pdf \
  "Compare this UI with the spec"
```

Compression is enabled by default for tool-heavy sessions. You can dedicate a
smaller model to compression:

```bash
agno-deep-agent --compression-model openai-responses:gpt-4o-mini \
  "Analyze the codebase and keep context compact"
```

## ACP For Editors

Run the same agent harness as an ACP stdio server:

```bash
agdeep acp --model ollama:gemma4:e4b --workspace /absolute/path/to/project
```

Use this command in ACP-compatible editors or local ACP clients. The editor
creates sessions and sends prompts over JSON-RPC; Agno Deep Agent responds with
plan, message, session metadata, and tool updates.

For editor-specific setup guidance (Zed, VS Code-compatible extensions,
JetBrains plugins, and Neovim clients), read
[ACP Editors](acp-editors.html).

## First Python Example

```bash
python examples/ollama_deep_agent.py
```

If you see `model not found`, confirm the exact model name with `ollama list`
and update `examples/ollama_deep_agent.py`.

## Next Step

Read [Models and Providers](models.html) to understand the supported providers.
