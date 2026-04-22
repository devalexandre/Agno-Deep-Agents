---
title: Architecture
---

# Architecture

Agno Deep Agent is an opinionated composition of Agno primitives.

## Components

```text
create_deep_agent()
        |
        v
Team(mode=TeamMode.tasks)
        |
        +-- Researcher
        +-- Implementer
        +-- Reviewer
        |
        +-- Skills(LocalSkills)
        +-- SqliteDb
        +-- CodingTools
```

## Leader

The `Team` acts as the leader. It:

- turns the user request into tasks;
- delegates to specialist members;
- stores context through the database;
- applies global instructions;
- exposes extra tools passed by the user.

## Members

| Member | Role |
| --- | --- |
| `Researcher` | Reads the workspace and identifies requirements, risks, and relevant files. |
| `Implementer` | Makes changes and runs allowed verification commands. |
| `Reviewer` | Checks regressions, tests, risks, and clarity. |

## Memory And Learning

All agents use the same `SqliteDb`. By default, the database lives at:

```text
.deep-agent/agno.db
```

This allows sessions, memories, and learnings to persist between runs.

## Workspace

File and shell tools use `CodingTools` with:

```python
restrict_to_base_dir=True
```

The base directory is the configured `workspace`. The default is the current
directory.

## Shell

The `Implementer` and `Reviewer` use shell tools with command allowlist and
timeout. This is useful for checks such as `python`, `pytest`, `git`, `grep`,
and `ls`.

To disable shell execution:

```bash
agno-deep-agent --no-shell "Review the project without running commands"
```

## What This Harness Does Not Try To Be

- It is not a container.
- It is not an operating-system sandbox.
- It does not replace human review for destructive or production operations.
- It does not hide Agno primitives; it chooses useful defaults.
