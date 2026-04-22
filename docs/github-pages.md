---
title: Publish On GitHub Pages
---

# Publish On GitHub Pages

The `docs/` directory is designed for the simplest GitHub Pages mode: publishing
directly from a branch.

## GitHub Setup

1. Open the repository on GitHub.
2. Go to `Settings`.
3. Open `Pages`.
4. Under `Build and deployment`, choose `Deploy from a branch`.
5. For `Branch`, choose `main`.
6. For the folder, choose `/docs`.
7. Save.

After a few minutes, GitHub Pages publishes the documentation.

## Configuration File

The site uses:

```text
docs/_config.yml
```

The visual layer is custom CSS using the same core Agno documentation tokens:

```text
primary: #FF4017
light background: #FFFFFF
dark background: #111113
font: Inter
```

The site also includes a persisted dark mode toggle and Rouge-compatible syntax
highlighting for fenced code blocks.

## Optional Local Preview

If you want to test with Jekyll locally, install Ruby/Jekyll and run from the
repository root:

```bash
bundle exec jekyll serve --source docs
```

Local preview is optional. GitHub Pages can render the Markdown files directly
when `/docs` is selected.

## Update Navigation

When you add a new page, link it from:

```text
docs/index.md
```

Also update:

```text
docs/_layouts/default.html
```
