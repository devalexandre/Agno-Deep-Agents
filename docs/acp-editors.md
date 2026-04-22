---
title: ACP Editors
---

# ACP Editors

This page documents how Agno Deep Agent works as an ACP server and how to wire
it to editors that support ACP through native features or compatible plugins.

## Current Support Level

Agno Deep Agent currently provides an ACP **stdio server** with the command:

```bash
agdeep acp --model ollama:gemma4:e4b --workspace /absolute/path/to/project
```

Implemented ACP methods:

- `initialize`
- `session/new`
- `session/load`
- `session/prompt`
- `session/cancel`

This means editor integrations are usable for real workflows, but still in an
early compatibility phase. Treat editor setup as **supported when the client can
start a stdio ACP server and speak these methods**.

## Shared Setup For Any Editor

1. Install the CLI so `agdeep` is available.
2. Pick a model (`--model ...`) that is already working in your environment.
3. Set `--workspace` to the repository root you want the agent to operate in.
4. Register the ACP server command in your editor/plugin ACP client settings.

Recommended command template:

```bash
agdeep acp --model ollama:gemma4:e4b --workspace /absolute/path/to/project
```

Optional flags you may also include:

- `--db-file /absolute/path/to/agno.db`
- `--skills-dir /absolute/path/to/skills`
- `--user-id your-stable-id`
- `--debug`

## Zed

Use a Zed ACP-compatible agent configuration and point the server command to
`agdeep acp`.

Configuration shape:

- transport: `stdio`
- command: `agdeep`
- args: `acp`, `--model`, `...`, `--workspace`, `...`

Validation checklist:

- Zed starts the subprocess successfully.
- First handshake calls `initialize`.
- Prompting starts ACP sessions (`session/new`) and turn execution
  (`session/prompt`).

## VS Code (ACP-Compatible Extensions)

Use a VS Code extension that supports ACP over stdio and configure the command
to launch Agno Deep Agent.

Configuration shape:

- transport: stdio
- command: `agdeep`
- args: `acp --model ... --workspace ...`

Validation checklist:

- Extension can connect and initialize.
- Prompt round-trips work with streamed updates.
- Cancel action maps to `session/cancel`.

## JetBrains IDEs

Use a JetBrains ACP-compatible plugin and register Agno Deep Agent as an ACP
server process.

Configuration shape:

- process command: `agdeep`
- process args: `acp --model ... --workspace ...`
- transport: stdio

Validation checklist:

- Session creation and load work.
- Prompt execution emits progress and final output.
- Cancellation returns control to the IDE promptly.

## Neovim

Use an ACP-capable Neovim plugin/client and set the server command to
`agdeep acp`.

Configuration shape:

- command list: `{ "agdeep", "acp", "--model", "...", "--workspace", "..." }`
- transport: stdio

Validation checklist:

- Client starts the process and performs `initialize`.
- Prompt requests map to `session/prompt`.
- Cancel command maps to `session/cancel`.

## Troubleshooting Integration

- If the editor cannot connect, run the same command in a terminal and check
  startup errors (model, environment, permissions, missing command).
- Always use an absolute workspace path in editor config.
- Keep stdout reserved for ACP protocol messages; logs should remain on stderr.
- If your editor expects additional ACP methods, verify compatibility with the
  currently implemented method set above.

## What Is Not Claimed Yet

- No claim of complete ACP feature parity across all editor clients.
- No claim that every plugin in each ecosystem already supports all server
  updates emitted by Agno Deep Agent.
- Richer progress mapping and broader client examples remain roadmap items.
