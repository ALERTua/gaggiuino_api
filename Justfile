# https://github.com/casey/just
set dotenv-load

set shell := ["powershell", "-c"]
set windows-shell := ["cmd", "/c"]

lint:
    uv run ruff format .
    uv run ruff check --fix
    uv run pre-commit run ty --all-files

pre:
    uv run pre-commit run --all-files

pre-update:
    uv run pre-commit autoupdate

build:
    del /s /q dist\*.tar.gz
    del /s /q dist\*.whl
    uv build

install:
    uv sync --all-groups

upgrade:
    uv sync --all-groups --upgrade

test:
    uv run pytest

test-e2e:
    uv run pytest -m e2e

uv-outdated *args:
    uv tree -d 1 --universal --outdated {{args}}

version VERSION:
    uv version {{VERSION}}
    just install
    just lint
    just pre
    just build

# Show available commands
help:
    @just --list
