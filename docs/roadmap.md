---
title: Roadmap
---

# Roadmap

The project should grow in small, useful layers. The priority is to stay simple
for CLI users while exposing deeper capabilities for editor, API, and automation
workflows.

## Now

- Installable CLI with `agno-deep-agent` and `agdeep`.
- Python API with `create_deep_agent`.
- OpenAI, local Ollama, Ollama Cloud, and Agno model strings.
- SQLite sessions, memory, and learning.
- Local skills.
- GitHub Pages documentation.
- ACP stdio server with `agdeep acp`.
- ACP editor integration guide for Zed, VS Code-compatible clients, JetBrains, and Neovim.

## Next

- ACP client config snippets per editor/plugin ecosystem.
- CLI profiles for reusable local configuration.
- Safer permission presets for shell and filesystem tools.
- Better session resume UX.
- More examples for coding, docs, and repository review.

## Planned

### ACP Adapter Improvements

Expose richer Agno Deep Agent progress over ACP for editor and IDE clients.

Current command:

```bash
agdeep acp --model ollama:gemma4:e4b --workspace .
```

Implemented:

- stdio server entrypoint;
- editor session to Agno session mapping;
- basic plan, message, session metadata, and tool updates.

Planned work:

- richer member and task progress events;
- stronger cancellation for long model/tool calls;
- editor-friendly file and shell events;
- Zed, VS Code, JetBrains, and Neovim examples.

### MCP Tool Loading

Attach MCP tools from a user config file without confusing MCP with ACP.

### AgentOS Example

Add an Agno-native deployment example for users who want an HTTP/API surface.

### Human Approval Policy

Add explicit approval rules for high-risk tool calls and destructive changes.

## Later

- Container or remote sandbox backend.
- Rich local event viewer.
- Packaged skill examples.
- CI for docs and package publishing.
