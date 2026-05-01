---
name: rust-programming
description: Rust development guidance for creating, modifying, reviewing, testing, packaging, and debugging Rust crates, CLIs, services, and libraries. Use when tasks involve .rs files, Cargo.toml, Cargo.lock, workspaces, ownership, lifetimes, traits, async Rust, tokio, serde, cargo fmt, cargo test, cargo clippy, or Rust dependency management.
---

# Rust Programming

## Goal

Make Rust changes that are explicit about ownership, error paths, feature flags,
and public API compatibility.

## Discovery

- Read `Cargo.toml`, `Cargo.lock`, workspace config, feature flags, examples,
  benches, and CI before editing.
- Inspect nearby modules and tests to understand error types, trait style,
  visibility, async runtime, and serialization conventions.
- Preserve crate boundaries and public API stability unless the user asks for a
  breaking change.

## Implementation

- Prefer clear ownership and borrowing over cloning; clone deliberately when it
  simplifies the API or avoids invalid lifetimes.
- Use `Result` and the crate's existing error approach (`thiserror`, `anyhow`,
  custom enums, or plain errors).
- Keep `unsafe` out of changes unless the project already requires it and the
  invariants are documented.
- Respect feature flags, `no_std`, platform-specific code, and workspace member
  boundaries.
- For async code, preserve the existing runtime and avoid blocking work on async
  executors.
- Keep trait bounds readable and introduce traits only when they reduce real
  coupling.

## Verification

- Run `cargo fmt` on changed Rust code.
- Run targeted `cargo test -p <crate>` or `cargo test <test-name>` first, then
  broader workspace tests when shared code changed.
- Use `cargo check` for fast validation and `cargo clippy` when configured or
  useful for the change.

## Review Focus

- Lifetime workarounds that hide ownership problems, accidental clones in hot
  paths, panics in library code, public API breaks, feature-gate regressions,
  async blocking, and lockfile changes unrelated to dependency edits.
