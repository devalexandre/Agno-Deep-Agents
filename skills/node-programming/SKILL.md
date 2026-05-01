---
name: node-programming
description: Node.js and JavaScript/TypeScript development guidance for creating, modifying, reviewing, testing, packaging, and debugging backend, CLI, tooling, and full-stack code. Use when tasks involve package.json, npm, pnpm, yarn, bun, .js, .mjs, .cjs, .ts, tsconfig, Express, NestJS, Next.js API routes, Vitest, Jest, ESLint, or Node dependency management.
---

# Node Programming

## Goal

Make Node.js changes that respect the project's runtime, module system, package
manager, and TypeScript strictness.

## Discovery

- Identify the package manager from lockfiles: `package-lock.json`,
  `pnpm-lock.yaml`, `yarn.lock`, or `bun.lockb`.
- Read `package.json` scripts, `tsconfig*.json`, lint config, test config, and
  framework conventions before editing.
- Preserve the existing module style: ESM, CommonJS, or mixed boundaries.
- Check whether the code targets Node only, browser bundles, serverless, or a
  full-stack framework.

## Implementation

- Prefer typed, explicit data flow in TypeScript; avoid weakening types with
  `any` unless the surrounding code already accepts it.
- Keep async code awaitable and handle rejected promises.
- Preserve environment variable conventions and validation patterns.
- Avoid switching package managers or adding dependencies unless the need is
  clear and the existing stack supports it.
- For HTTP APIs, keep route, validation, service, and test changes aligned.
- For CLIs, preserve exit codes, stdout/stderr conventions, and non-interactive
  behavior.

## Verification

- Use the project's scripts first: `npm test`, `pnpm test`, `yarn test`,
  `bun test`, `npm run lint`, `npm run typecheck`, or `npm run build`.
- Prefer targeted tests before full suites when the project is large.
- If dependencies are missing, run syntax or TypeScript checks that are available
  and report the gap clearly.

## Review Focus

- ESM/CJS mismatches, unhandled promises, accidental browser-only or Node-only
  imports, broken build scripts, unsafe environment access, dependency churn, and
  generated lockfile noise.
