# gaggiuino_api — agent guidelines

Async Python wrapper (aiohttp) for the Gaggiuino espresso machine REST API.
Published, typed library — treat the public API as stable unless breaking changes are explicitly allowed.

## Project memory

Read `.claude/memory/MEMORY.md` before each task. It holds the project memory: the Python version policy, the upstream API documentation, the test machine and the plans. When a task touches a topic of an index line, read the file of that line.

## Facts you can't derive from the repo

- Dev machine is Windows, CI is Linux: keep committed files LF with forward-slash paths
  (`.gitattributes` enforces eol; platform-dependent content flip-flops CI).
- E2E tests (test/e2e/, marker `e2e`, deselected by default) need real hardware:
  `uv run pytest -m e2e test/e2e`. Env: `GAGGIUINO_BASE_URL` (default `http://gaggiuino.local`).
  They follow Read -> Modify -> Verify -> Restore: never leave the machine in a modified state.
  A test writes only the `led` and `display` settings groups and deletes only the profile copy
  that it created. It never sends a DELETE for an id that the machine does not have, never calls
  `firmware.update()` and never deletes a shot.

## Workflow

- Task runner is just; see Justfile or `just help` for recipes and prefer them over raw commands.
- Verification gate for any change: `just pre` (ruff, ty, pytest, eof/eol fixers) — run it
  after code changes and fix what it finds.
- Dependencies: `uv add` / `uv add --dev`, never edit pyproject.toml by hand;
  check outdated with `just uv-outdated`.
- Never stage or commit unless directly asked; propose a commit message
  (Conventional Commits) after each task instead.
- Only the user bumps the version — never do it, only remind when a changeset looks release-worthy.
- Ask open questions before implementing; when working through a list, show per-item
  statuses after each item.
- New behavior gets a short README example. Tests only where they validate a fix or new
  behavior — minimal and focused.

## Code patterns

- Resources: classes in `resources/` that take the transport, for example `Profiles` and `Shots`.
  A method accepts a model object or an id and returns a model, an `int` or `None`. A failure
  raises an exception from `exceptions.py`. Follow the neighbours.
- Models: frozen dataclasses in `models/` on the base class `Model`. Each field is declared with
  `api("firmwareName")`, and the model has `from_api()` (tolerant to unknown keys from newer
  firmware) and `to_api()`.
- Public names are exported in `__init__.py` (`__all__` is sorted).

## Responses

- Be concise. Use Markdown.

Last updated: 2026-11-13
