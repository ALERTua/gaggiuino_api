# https://github.com/casey/just
set dotenv-load

set shell := ["powershell", "-c"]
set windows-shell := ["cmd", "/c"]

lint:
    uv run ruff format .
    uv run ruff check --fix

pre *args:
    uv run pre-commit run {{args}}

pre-all *args:
    just pre --all-files {{args}}

pre-upgrade:
    uv run pre-commit autoupdate

build:
    del /s /q dist\*.tar.gz
    del /s /q dist\*.whl
    uv build

install:
    uv sync --dev --upgrade

version VERSION:
    uv version {{VERSION}}
    just install
    just lint
    just pre
    just build

# Show available commands
help:
    @just --list
