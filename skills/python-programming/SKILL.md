---
name: python-programming
description: Python development guidance for creating, modifying, reviewing, testing, packaging, and debugging Python code. Use when tasks involve .py files, pyproject.toml, requirements files, pytest, ruff, mypy, FastAPI, Django, Flask, CLIs, scripts, type hints, virtual environments, or Python dependency management.
---

# Python Programming

## Goal

Produce Python changes that fit the local project style, remain easy to test,
and avoid surprising runtime behavior.

## Discovery

- Identify the Python version, package manager, and tooling from `pyproject.toml`,
  `setup.cfg`, `setup.py`, `requirements*.txt`, lockfiles, tox/nox config, and CI.
- Check existing module layout before adding files.
- Read nearby tests, fixtures, factories, and public API docs before changing
  behavior.
- Preserve the project's existing framework choices, import style, typing level,
  and error handling conventions.

## Implementation

- Prefer straightforward functions and small classes over new abstractions.
- Use `pathlib`, context managers, dataclasses, enums, and type hints when they
  match the surrounding code.
- Keep import-time side effects out of modules; put executable script entry
  points behind `if __name__ == "__main__":`.
- For async code, preserve the current event-loop model and avoid blocking calls
  inside coroutines.
- For web apps, update schemas, route handlers, services, and tests together so
  request and response contracts stay aligned.
- For packaging changes, keep dependencies minimal and update the right
  manifest or lockfile for the repo's chosen tool.

## Verification

- Prefer the narrowest relevant checks first: targeted `pytest`, then broader
  test suites when the change crosses modules.
- Run configured formatters and linters such as `ruff`, `black`, `isort`, and
  `mypy` only when they are already part of the project.
- When dependencies are unavailable, run syntax checks such as
  `python -m py_compile <files>` and explain the remaining gap.

## Review Focus

- Import cycles, hidden global state, mutable defaults, broad exception catches,
  sync/async mismatches, unclosed files, and compatibility with the configured
  Python version.
