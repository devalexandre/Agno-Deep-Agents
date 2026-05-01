---
name: go-programming
description: Go development guidance for creating, modifying, reviewing, testing, and debugging Go services, libraries, CLIs, and tooling. Use when tasks involve .go files, go.mod, go.work, goroutines, channels, contexts, HTTP handlers, database code, table tests, gofmt, go test, or Go module management.
---

# Go Programming

## Goal

Make idiomatic Go changes with small APIs, explicit errors, and verification
through the standard toolchain.

## Discovery

- Read `go.mod`, `go.work`, build tags, Makefiles, CI, and package layout before
  choosing commands or dependencies.
- Inspect nearby packages and tests to infer naming, error wrapping, logging,
  context use, and dependency injection style.
- Preserve public API compatibility unless the user explicitly requests a break.

## Implementation

- Keep packages cohesive and avoid utility packages unless the repo already uses
  them.
- Return errors explicitly; wrap with context where the caller needs it.
- Pass `context.Context` through request, database, network, and long-running
  operations.
- Keep interfaces small and define them near the consumer.
- Use goroutines, channels, mutexes, and wait groups only when concurrency is
  needed and lifecycle/cancellation are clear.
- Avoid global mutable state; if unavoidable, isolate it and protect concurrent
  access.
- Run `gofmt` on changed Go files.

## Testing

- Prefer table-driven tests for branching behavior.
- Use existing test helpers and fixtures before inventing new ones.
- Run targeted `go test ./path/...` first, then broader `go test ./...` when the
  change affects shared packages.
- Consider `go test -race` for concurrency changes and `go vet` or configured
  linters when the project already uses them.

## Review Focus

- Missing context cancellation, goroutine leaks, unchecked errors, nil pointer
  paths, data races, unintended exported symbols, and accidental changes to
  module files.
