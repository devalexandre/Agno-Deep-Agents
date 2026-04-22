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

## Structure

```text
skills/
+-- codebase-analysis/
|   +-- SKILL.md
+-- deep-agent-planning/
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
