---
title: Get Started
---

# Get Started

This guide gets Agno Deep Agent running locally.

## Requirements

- Python 3.11 or newer.
- A model available through OpenAI or Ollama.
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

## First Python Example

```bash
python examples/ollama_deep_agent.py
```

If you see `model not found`, confirm the exact model name with `ollama list`
and update `examples/ollama_deep_agent.py`.

## Next Step

Read [Models and Ollama](models.html) to understand the supported providers.
