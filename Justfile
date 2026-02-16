# https://github.com/casey/just
set dotenv-load

# Set shell for non-Windows OSs:
set shell := ["powershell", "-c"]

# Set shell for Windows OSs:
set windows-shell := ["cmd", "/c"]

# Run pre-commit
lint:
    uv run ruff format .
    uv run ruff check --fix

pre:
    uv run pre-commit run --all-files

build:
    del /s /q dist\*.tar.gz
    del /s /q dist\*.whl
    uv build

install:
    uv sync --dev --upgrade

# Update version across all files
version VERSION:
    uv version {{VERSION}}
    just install
    just lint
    just pre
    just build

# Show available commands
help:
    @just --list
