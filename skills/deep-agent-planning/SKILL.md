---
name: deep-agent-planning
description: Planning discipline for long-running Deep Agent tasks with delegation, task tracking, validation, and concise delivery.
metadata:
  version: "0.2.0"
  tags: ["planning", "delegation", "deep-agents"]
---

# Deep Agent Planning

Use this skill when the user asks for a complex, multi-step task, especially when
the work may require reading files, editing code, running checks, or coordinating
specialist agents.

## Goal

Keep long-running work moving without losing the thread. Make plans explicit
enough for a small local model, but flexible enough for a larger reasoning model.

## Operating Loop

1. Clarify the concrete goal, constraints, and expected deliverable from the user
   request and visible project context.
2. Create a compact task list with discovery, implementation, validation, and
   final reporting steps.
3. Do discovery before editing unless the change target is already obvious.
4. Delegate discovery to a research-focused member when it will reduce risk.
5. Delegate implementation only after the relevant files and constraints are known.
6. Delegate review after implementation to look for regressions, missing tests,
   and unclear user-facing behavior.
7. Keep the task loop moving until the goal is complete or a real blocker appears.

## Planning Format

Use this internal structure for non-trivial work:

- Goal: one sentence.
- Constraints: workspace, shell policy, model limits, user preferences, attached
  media, external docs, compatibility needs.
- Steps: discover, implement, verify, report.
- Done means: the observable condition that proves the task is complete.

## Delegation Rules

- Researcher: use for mapping files, docs, risks, and unknowns.
- Implementer: use for scoped edits only after target files are known.
- Reviewer: use after edits or when the task is a review.
- Avoid delegation when a direct single-step answer is enough.
- Do not ask multiple members to do the same investigation.

## Context Rules

- Prefer direct evidence from files, tool outputs, and documented project patterns.
- Load additional skill instructions only when the task matches the skill summary.
- Preserve useful project facts, decisions, user preferences, and unfinished task
  context in memory when they are likely to matter in later sessions.
- When Agno compression is enabled, treat compressed tool output as a lossy
  summary. Re-read source files before exact edits, quotes, or line-specific
  claims.
- When multimodal inputs are attached, identify which media affects the plan and
  which model capability is required.
- Keep the final answer short and grounded: what changed, what was verified, and
  what risk remains.

## Small Model Mode

For 3B or otherwise small models:

- Use plain, imperative steps.
- Keep prompts short and avoid nested requirements.
- Prefer explicit success criteria over "do the right thing" language.
- Ask for clarification only when the next action could cause data loss,
  external side effects, or a wrong public API.
- Validate frequently with small checks instead of relying on memory.

## Filesystem And Shell

- Treat filesystem tools as workspace-bound.
- Do not imply that workspace restrictions are equivalent to a full OS or container
  sandbox.
- Use shell commands for targeted verification when enabled.
- If shell is disabled or a command is blocked by policy, continue with file-based
  inspection and say what was not verified.
- For startup commands or direct shell requests, keep command output separate
  from the agent's reasoning unless the user pipes or includes it in the prompt.

## Final Delivery

Answer in the user's language. Prefer this shape:

- Outcome: what was completed.
- Verification: commands or checks run.
- Remaining risk: only meaningful gaps, not generic caveats.
