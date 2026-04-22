---
title: Models and Ollama
---

# Models and Ollama

The harness accepts model strings in `provider:model` format.

## Providers

| Provider | Example | Behavior |
| --- | --- | --- |
| `openai-responses` | `openai-responses:gpt-5.2` | Uses `OpenAIResponses`. |
| `responses` | `responses:gpt-5.2` | Alias for `openai-responses`. |
| `openai` | `openai:gpt-5.2` | Uses Agno's default OpenAI provider. |
| `ollama` | `ollama:gemma4:e4b` | Uses local Ollama at `http://localhost:11434`. |
| `ollama-responses` | `ollama-responses:gpt-oss:20b` | Uses Ollama's local Responses endpoint. |
| `ollama-cloud` | `ollama-cloud:devstral-2` | Uses the Ollama cloud behavior. |

If the string has no provider, for example `gpt-5.2`, the harness uses
`OpenAIResponses`.

## Local Ollama By Default

In Agno, the `Ollama` model class can use Ollama Cloud when `OLLAMA_API_KEY` is
present and no `host` is provided.

To avoid surprises, Agno Deep Agent defines:

```text
ollama:* -> http://localhost:11434
```

Cloud must be explicit:

```text
ollama-cloud:devstral-2
```

## Check Local Models

Use:

```bash
ollama list
```

The model name passed to the harness must match the `NAME` column exactly.

Example:

```text
gemma4:e4b
```

should be used as:

```bash
agno-deep-agent --model ollama:gemma4:e4b "Say hello"
```

## Custom Host

```bash
agno-deep-agent --model ollama:gemma4:e4b \
  --ollama-host http://192.168.1.10:11434 \
  "Analyze the project"
```

## When To Use `ollama-responses`

Use `ollama-responses:*` when you want Ollama's OpenAI-compatible
`/v1/responses` endpoint. It requires an Ollama version that supports that
endpoint.
