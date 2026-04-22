---
title: Protocols
---

# Protocols

Protocols define how Agno Deep Agent should connect to tools, editors, and
runtime surfaces. The project does not implement every protocol yet; this page
keeps the direction explicit.

## ACP

Agent Client Protocol standardizes communication between coding agents and code
editors or IDEs. The useful integration model for this project is:

```text
Editor or IDE
      |
      | ACP over stdio
      v
Agno Deep Agent ACP server
      |
      v
Agno Team(mode=tasks)
```

ACP is a good fit when the editor owns project context and the agent should send
rich progress, content, file, terminal, and plan updates back to the editor.

Current status: initial stdio server implemented.

Command:

```bash
agdeep acp --model ollama:gemma4:e4b --workspace .
```

Implemented methods:

- `initialize`
- `session/new`
- `session/load`
- `session/prompt`
- `session/cancel`

The adapter maps ACP sessions to Agno `session_id` values, runs the existing
Agno `Team(mode=tasks)` harness, emits basic plan/message/tool updates through
`session/update`, and keeps stdout reserved for ACP JSON-RPC messages.

Planned clients:

- Zed custom agent server.
- Visual Studio Code through ACP-compatible extensions.
- JetBrains IDEs.
- Neovim through ACP-compatible plugins.

See [ACP Editors](acp-editors.html) for practical setup guidance and current
support expectations by editor ecosystem.

## MCP

Model Context Protocol is different from ACP. MCP is for tools and context
servers that an agent can call. ACP is for editor/client integration.

The future MCP shape for this project should be:

```bash
agdeep --mcp-config ./mcp.json "Review the repository"
```

Current status: planned.

## AgentOS

AgentOS is the Agno-native path for serving agents as production APIs. It is a
better fit than ACP when the goal is HTTP deployment, API integration, runtime
visibility, or a hosted application surface.

Current status: example planned.

## What We Should Avoid

- Do not present ACP as complete editor integration until client examples and
  richer event handling exist.
- Do not mix ACP and MCP concepts in the CLI.
- Do not bypass the existing Agno `Team`, memory, skills, and tool patterns.
- Do not add protocol dependencies to the default install until the integration
  is useful.

## Implementation Notes

An ACP adapter should translate between editor sessions and Agno sessions:

| ACP concept | Agno Deep Agent concept |
| --- | --- |
| Client session | `session_id` |
| User prompt turn | `Team.run` |
| Progress events | Team/member stream events |
| File context | Workspace-bound `CodingTools` |
| Terminal events | Restricted shell tool calls |
| Agent plan | Task list from `TeamMode.tasks` |

This keeps the protocol layer thin and preserves the Agno-native internals.
