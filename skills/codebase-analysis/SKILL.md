---
name: codebase-analysis
description: Analyze a codebase before changing it, infer local patterns, and choose focused implementation and verification steps.
metadata:
  version: "0.1.0"
  tags: ["code", "analysis", "testing"]
---

# Codebase Analysis

Use this skill when the task involves reading, changing, reviewing, or explaining
code.

## Discovery

1. List or search files to understand the project shape.
2. Read the smallest set of files that define the behavior being changed.
3. Identify the framework, dependency style, test layout, and existing naming
   conventions.
4. Look for nearby tests or examples before adding new behavior.

## Implementation

- Prefer existing abstractions and local conventions.
- Keep edits narrow and reversible.
- Avoid broad refactors unless the requested change requires them.
- Add helper functions only when they reduce real complexity.
- Update documentation when the public usage changes.

## Verification

- Run the most targeted available checks first.
- If dependencies or API keys are missing, still run syntax or import checks that
  do not require external services.
- Report exactly which checks ran and which checks could not run.

## Review

Focus review comments on:

- Incorrect behavior or edge cases.
- Regressions from existing behavior.
- Missing tests for risky logic.
- Security or sandbox assumptions that are stronger than the implementation.
