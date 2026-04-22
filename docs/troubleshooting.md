---
title: Troubleshooting
---

# Troubleshooting

## `model not found` With Ollama

Common error:

```text
model 'gemma4:e4b' not found (status code: 404)
```

Check:

```bash
ollama list
```

The model name must match the name shown by Ollama exactly.

## `OLLAMA_API_KEY` Is Set, But I Want Local Ollama

Use `ollama:<model>`. The harness forces `http://localhost:11434` by default:

```bash
agno-deep-agent --model ollama:gemma4:e4b "Say hello"
```

For cloud, use `ollama-cloud:<model>`.

## Ollama Runs On Another Host

Pass `--ollama-host`:

```bash
agno-deep-agent --model ollama:gemma4:e4b \
  --ollama-host http://localhost:11434 \
  "Say hello"
```

## `OPENAI_API_KEY is not set`

This warning appears when the provider is OpenAI:

```bash
export OPENAI_API_KEY="your-key-here"
```

Or use local Ollama:

```bash
agno-deep-agent --model ollama:gemma4:e4b "Say hello"
```

## The Agent Tried To Run A Blocked Command

`CodingTools` blocks commands outside the allowlist and dangerous shell
operators in restricted mode. For a more conservative run, disable shell:

```bash
agno-deep-agent --no-shell "Analyze the files without running commands"
```

## Memory Does Not Seem To Persist

Confirm that you are using the same `--db-file`, `--user-id`, and `--session-id`.

Example:

```bash
agno-deep-agent --user-id dev@example.com --session-id local-project \
  "Remember that I prefer concise answers"

agno-deep-agent --user-id dev@example.com --session-id local-project \
  "Continue the session"
```

## GitHub Pages Did Not Update

Check:

- `Settings > Pages` points to branch `main` and folder `/docs`.
- `docs/index.md` exists.
- The latest deploy in `Actions` completed successfully.
- Your browser cache is not showing an old version.
