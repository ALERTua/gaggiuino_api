Junie Guidelines for gaggiuino_api

Purpose
- This document defines how Junie should work within this repository to make safe, minimal, and maintainable changes.

Repository Basics
- Language/Version: Python 3.13
- Python version always follows the one that Home Assistant project uses
- Packaging: PEP 621 via pyproject.toml, src layout
- Testing: pytest (asyncio auto mode)
- Lint/Format: ruff (check + format)
- Task runner: tox

Core Principles
1. Make the minimal change necessary to satisfy the issue.
2. Keep a clear audit trail: explain findings, plan, and next steps in each response.
3. Prefer small, focused commits/patches.
4. Match the existing style and tooling, but propose more modern tools if necessary.
5. Keep cross-platform safety in mind.

How Junie Communicates (Process Contract)
- Every response contains exactly two parts:
  1) `UPDATE` block with:
     - `PREVIOUS_STEP`: Brief summary of new outcomes and observations since last step.
     - `PLAN`: Numbered list with progress marks: ✓ = done, * = in progress, ! = failed.
     - `NEXT_STEP`: What you will do next.
  2) An immediate tool call aligned with `NEXT_STEP`.
- Use specialized tools (search_project, get_file_structure, open, create, search_replace, submit) instead of generic shell where possible.
- Do not mix special tools and terminal commands in one call.
- Do not create files outside the repository.
- Use Windows backslashes in paths.

Coding Standards
- Linting/formatting: ruff is the source of truth.
  - Run: tox -e lint (ruff check .; ruff format --check .)
  - If formatting changes are required, apply ruff format locally before committing (or propose the minimal needed edits).
- Line length: 120 (pycodestyle), docstring code blocks line length: 88.
- Quote style: preserve (do not churn quotes unnecessarily).
- Keep import placement consistent; __init__.py may ignore E402.
- Typing: Maintain or improve type hints; project is typed (py.typed present).

Tests
- Run unit tests via tox:
  - asyncio mode is auto; default fixture loop scope is session.
- Add tests only when necessary to validate a bugfix or new behavior; keep them minimal and focused.

Files and Structure
- Source code lives under src/gaggiuino_api/.
- Tests live under test/.
- Keep images, scripts, and dist artifacts as-is unless an issue requires changes.

API and Backward Compatibility
- This is a published library; treat API as stable unless the issue explicitly allows breaking changes.
- If a change affects public interfaces, document it in README and consider version bump policy below.

Versioning and Releases
- Version is defined in pyproject.toml.
- You are not allowed to bump the version number unless directly asked.

Documentation
- README.md is the main documentation. Keep examples accurate and minimal.
- If you add new behavior, update README.md with a short example.

Commit/PR Hygiene
- Commit messages: concise, imperative subject line; include why when not obvious.
- Keep diffs small and focused on the issue.
- After each Task propose a commit message for the resulting changeset.

Common Tasks Cheat Sheet
- Add a new module:
  - Place under src/gaggiuino_api/.
  - Include typing and ruff-compliant style.
  - Add minimal tests under test/ if behavior is non-trivial.
- Fix a bug:
  - Reproduce with a failing test when possible.
  - Implement the smallest fix.
  - Run `tox`.
- Update docs only:
  - Edit README.md and run lint to ensure no trailing whitespace or formatting nits.
- If you need to add a new dependency, add it via `uv add`, and not via plain pyproject.toml edit.
  - Don't forget to uv lock afterwards.
- To check for outdated dependencies use `uv_outdated.cmd` which is found in PATH.

Windows Path and Shell Notes
- Use backslashes in any paths you add to code snippets or scripts.
- PowerShell semantics apply for shell command examples in repo scripts.

Safety Checks Before Submit
- Ensure: `tox` passes.
- Ensure: changes are minimal and directly address the issue.

Last updated: 2025-08-17
