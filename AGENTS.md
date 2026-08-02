# gaggiuino_api — agent guidelines

Async Python wrapper (aiohttp) for the Gaggiuino espresso machine REST API.
Published, typed library — treat the public API as stable unless breaking changes are explicitly allowed.

## Facts you can't derive from the repo

- Python version policy: follows [Home Assistant Core](https://github.com/home-assistant/core/blob/dev/pyproject.toml).
- Upstream API reference: https://gaggiuino.github.io/rest-api/rest-api.md — fetch the raw
  markdown; the rendered site loads content via JS and scrapes empty.
- Dev machine is Windows, CI is Linux: keep committed files LF with forward-slash paths
  (`.gitattributes` enforces eol; platform-dependent content flip-flops CI).
- E2E tests (test/e2e/, marker `e2e`, deselected by default) need real hardware:
  `uv run pytest -m e2e test/e2e`. Env: `GAGGIUINO_BASE_URL`, `GAGGIUINO_PROFILE_OFF`,
  `GAGGIUINO_PROFILE_TEST`. They must follow Read -> Modify -> Verify -> Restore —
  never leave the machine in a modified state.

## Workflow

- Task runner is just; see Justfile or `just help` for recipes and prefer them over raw commands.
- Verification gate for any change: `just pre-all` (ruff, ty, pytest, eof/eol fixers) — run it
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

- Endpoint wrappers: methods on GaggiuinoAPI (api.py) that accept a model object or id
  and return a model, None, or bool — follow the neighbours.
- Models: frozen dataclasses (models.py) with `from_dict()` tolerant to unknown keys from
  newer firmware, and `to_api_dict()` where POST is supported. Export via __init__.py
  (`__all__` is sorted).

## Responses

- Be concise. Use Markdown.

Last updated: 2026-08-02
