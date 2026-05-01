---
title: Skills
---

# Skills

Skills are loaded from the `skills/` directory through `LocalSkills`.

## Included Skills

| Skill | Use |
| --- | --- |
| `deep-agent-planning` | Planning, delegation, validation, and final delivery. |
| `codebase-analysis` | Codebase reading, local pattern inference, and verification. |
| `python-programming` | Python implementation, tests, packaging, and review. |
| `go-programming` | Go implementation, modules, tests, and concurrency review. |
| `node-programming` | Node.js, JavaScript, TypeScript, package scripts, and builds. |
| `elixir-programming` | Elixir, Phoenix, OTP, Ecto, and ExUnit workflows. |
| `rust-programming` | Rust crates, ownership, Cargo checks, and API review. |
| `social-video-shorts` | Cut source videos into social-platform short clips. |

## Structure

```text
skills/
+-- codebase-analysis/
|   +-- SKILL.md
+-- elixir-programming/
|   +-- SKILL.md
+-- go-programming/
|   +-- SKILL.md
+-- deep-agent-planning/
|   +-- SKILL.md
+-- node-programming/
|   +-- SKILL.md
+-- python-programming/
|   +-- SKILL.md
+-- rust-programming/
|   +-- SKILL.md
+-- social-video-shorts/
    +-- SKILL.md
```

## Create A New Skill

Create a directory under `skills/`:

```text
skills/my-skill/SKILL.md
```

Minimal example:

```markdown
---
name: my-skill
description: When this skill should be used.
metadata:
  version: "0.1.0"
  tags: ["example"]
---

# My Skill

Use this skill when...
```

## Use Another Directory

Via CLI:

```bash
agno-deep-agent --skills-dir ./my-skills "Run the task"
```

Via Python:

```python
from agno_deep_agents import create_deep_agent


agent = create_deep_agent(skills_dir="./my-skills")
```

## Best Practices

- Keep the `description` clear; it guides progressive discovery.
- Keep scripts and references near `SKILL.md` when needed.
- Prefer small, actionable skills.
- Avoid turning a skill into broad generic documentation.
