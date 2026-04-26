---
name: codebase-analysis
description: Analyze a codebase before changing it, infer local patterns, and choose focused implementation and verification steps.
metadata:
  version: "0.2.0"
  tags: ["code", "analysis", "testing"]
---

# Codebase Analysis

Use this skill when the task involves reading, changing, reviewing, or explaining
code.

## Goal

Build confidence from local evidence before changing code. This skill favors
small, repeatable investigation steps that work with both small local models and
larger hosted models.

## Operating Rules

- Do not guess project structure when files can be listed or searched.
- Prefer exact file paths, symbols, commands, and test names over summaries.
- Keep each step narrow: read only the files needed for the next decision.
- State assumptions explicitly when evidence is incomplete.
- If attached images, audio, video, or files are relevant, mention what they are
  being used to decide.

## Discovery Checklist

1. List or search files to understand the project shape.
2. Read the smallest set of files that define the behavior being changed.
3. Identify the framework, dependency style, test layout, and existing naming
   conventions.
4. Look for nearby tests or examples before adding new behavior.
5. Check docs, config, entry points, and public APIs when the change affects
   usage.
6. Summarize the evidence before editing: relevant files, current behavior,
   likely change location, and verification target.

## Small Model Mode

When the selected model is small or local:

- Use short numbered plans with one action per line.
- Avoid multi-hop assumptions. Read the next file instead.
- Prefer concrete instructions like "edit this function" over abstract goals.
- Keep intermediate summaries brief so context compression preserves the facts.
- Re-check exact code before final edits if tool results were compressed.

## Implementation

- Prefer existing abstractions and local conventions.
- Keep edits narrow and reversible.
- Avoid broad refactors unless the requested change requires them.
- Add helper functions only when they reduce real complexity.
- Update documentation when the public usage changes.
- Preserve backwards-compatible CLI/API behavior unless the user explicitly asks
  for a break.
- For user-facing CLI changes, update help text and at least one usage example.

## Verification

- Run the most targeted available checks first.
- If dependencies or API keys are missing, still run syntax or import checks that
  do not require external services.
- Report exactly which checks ran and which checks could not run.
- For prompt/instruction-only changes, verify importability or construction when
  full model calls are not practical.
- For multimodal behavior, verify argument parsing and object construction even
  if the chosen model cannot process that media type.

## Review

Focus review comments on:

- Incorrect behavior or edge cases.
- Regressions from existing behavior.
- Missing tests for risky logic.
- Security or sandbox assumptions that are stronger than the implementation.
- Differences between advertised CLI behavior and actual SDK support.
- Cases where a small model may miss a hidden assumption or overloaded prompt.

## Final Report

Keep the final answer compact:

- What changed.
- What was verified.
- What could not be verified and why.
- Any follow-up that would materially reduce risk.
