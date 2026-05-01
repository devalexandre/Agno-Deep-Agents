---
title: Models and Providers
---

# Models and Providers

The harness accepts model strings in `provider:model` format.

Agno Deep Agent keeps a few special cases for OpenAI Responses and Ollama, then
delegates the rest to Agno's native model-string resolver. That means the same
format works in the CLI, `/model`, `--compression-model`, and the Python SDK.

If the string has no provider, for example `gpt-5.2`, the harness uses
`OpenAIResponses`.

## Common Providers

| Provider | Example | Requirement |
| --- | --- | --- |
| `openai-responses` | `openai-responses:gpt-5.2` | `OPENAI_API_KEY` |
| `openai` | `openai:gpt-4o` | `OPENAI_API_KEY` |
| `anthropic` | `anthropic:claude-sonnet-4-5` | `ANTHROPIC_API_KEY` |
| `google` | `google:gemini-3-flash-preview` | `GOOGLE_API_KEY` or Vertex AI |
| `groq` | `groq:llama-3.3-70b-versatile` | `GROQ_API_KEY` |
| `mistral` | `mistral:mistral-large-latest` | `MISTRAL_API_KEY` |
| `deepseek` | `deepseek:deepseek-chat` | `DEEPSEEK_API_KEY` |
| `xai` | `xai:grok-3` | `XAI_API_KEY` |
| `perplexity` | `perplexity:sonar-pro` | `PERPLEXITY_API_KEY` |
| `cohere` | `cohere:command-a-03-2025` | `CO_API_KEY` |
| `together` | `together:meta-llama/Llama-3-70b-chat-hf` | `TOGETHER_API_KEY` |
| `fireworks` | `fireworks:accounts/fireworks/models/llama-v3p1-70b-instruct` | `FIREWORKS_API_KEY` |
| `openrouter` | `openrouter:anthropic/claude-3.5-sonnet` | `OPENROUTER_API_KEY` |
| `litellm` | `litellm:gpt-4o` | Provider-specific key |
| `azure-ai-foundry` | `azure-ai-foundry:gpt-4o` | Azure AI Foundry credentials |
| `ollama` | `ollama:gemma4:e4b` | Local Ollama |
| `ollama-responses` | `ollama-responses:gpt-oss:20b` | Local Ollama Responses |
| `ollama-cloud` | `ollama-cloud:devstral-2` | `OLLAMA_API_KEY` |

Inside the interactive CLI, use:

```text
/models
/m anthropic:claude-sonnet-4-5
```

The `/model ...` command saves the selection in `.deep-agent/config.json` for
the active workspace. Later runs use that saved model until another `/model ...`
command changes it. The `--model ...` flag remains a one-run override, and
`DEEP_AGENT_MODEL` is used when no workspace model has been saved.

Agno supports additional native, local, cloud, gateway, and aggregator
providers. See the official [Agno model-string docs](https://docs.agno.com/models/model-as-string)
and [Agno provider index](https://docs.agno.com/models/providers/model-index)
for the current list and provider-specific setup.

## Provider Dependencies

The base install includes the default OpenAI and Ollama SDKs. Some providers
need their own SDK package in the active environment, for example:

```bash
pip install anthropic google-genai groq mistralai cohere together litellm
```

If a provider backend is missing, the CLI prints a targeted install hint when
one is known, or points you back to the Agno provider docs.

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
