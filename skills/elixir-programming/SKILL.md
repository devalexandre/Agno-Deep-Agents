---
name: elixir-programming
description: Elixir development guidance for creating, modifying, reviewing, testing, and debugging Elixir and Phoenix applications. Use when tasks involve .ex or .exs files, mix.exs, Phoenix, LiveView, Ecto, OTP supervision trees, GenServer, ExUnit, mix format, mix test, migrations, schemas, contexts, or Elixir dependency management.
---

# Elixir Programming

## Goal

Make idiomatic Elixir changes that preserve clear data flow, OTP boundaries, and
project conventions.

## Discovery

- Read `mix.exs`, `.formatter.exs`, config files, supervision trees, contexts,
  schemas, and nearby tests before editing.
- Identify whether the project is a library, Mix app, Phoenix app, umbrella, or
  release-oriented service.
- Follow existing context boundaries, naming, aliases, and error tuple style.

## Implementation

- Prefer pattern matching, guards, pipelines, and small pure functions over
  deeply nested conditionals.
- Return `{:ok, value}` and `{:error, reason}` consistently where the project
  uses result tuples.
- Keep side effects at process, boundary, or adapter layers.
- For OTP code, make ownership, supervision, restart behavior, and message
  handling explicit.
- For Ecto, update schemas, changesets, migrations, contexts, and tests together.
- For Phoenix and LiveView, keep params, assigns, events, templates, and tests in
  sync.

## Verification

- Run `mix format` for changed Elixir files.
- Run targeted `mix test path/to/test.exs` first, then broader `mix test` when
  shared behavior changed.
- Use `mix compile --warnings-as-errors` when the project or CI expects warning
  cleanliness.

## Review Focus

- Broken pattern matches, atom leaks from external input, process mailbox growth,
  missing supervision, migration/schema drift, fragile LiveView assigns, and
  tests that depend on global process state.
