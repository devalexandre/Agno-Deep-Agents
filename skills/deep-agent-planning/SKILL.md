---
name: deep-agent-planning
description: Planning discipline for long-running Deep Agent tasks with delegation, task tracking, validation, and concise delivery.
metadata:
  version: "0.1.0"
  tags: ["planning", "delegation", "deep-agents"]
---

# Deep Agent Planning

Use this skill when the user asks for a complex, multi-step task, especially when
the work may require reading files, editing code, running checks, or coordinating
specialist agents.

## Operating Loop

1. Clarify the concrete goal, constraints, and expected deliverable from the user
   request and visible project context.
2. Create a compact task list with discovery, implementation, validation, and
   final reporting steps.
3. Delegate discovery to a research-focused member before editing.
4. Delegate implementation only after the relevant files and constraints are known.
5. Delegate review after implementation to look for regressions, missing tests,
   and unclear user-facing behavior.
6. Keep the task loop moving until the goal is complete or a real blocker appears.

## Context Rules

- Prefer direct evidence from files, tool outputs, and documented project patterns.
- Load additional skill instructions only when the task matches the skill summary.
- Preserve useful project facts, decisions, user preferences, and unfinished task
  context in memory when they are likely to matter in later sessions.
- Keep the final answer short and grounded: what changed, what was verified, and
  what risk remains.

## Filesystem And Shell

- Treat filesystem tools as workspace-bound.
- Do not imply that workspace restrictions are equivalent to a full OS or container
  sandbox.
- Use shell commands for targeted verification when enabled.
- If shell is disabled or a command is blocked by policy, continue with file-based
  inspection and say what was not verified.
