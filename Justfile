# https://github.com/casey/just
set dotenv-load

# Set shell for non-Windows OSs:
set shell := ["powershell", "-c"]

# Set shell for Windows OSs:
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# Run pre-commit
lint:
    uv run ruff format .
    uv run ruff check --fix

pre:
    uv run pre-commit run --all-files

install:
    uv sync --dev --upgrade

# Update version across all files
version VERSION:
    uv version {{VERSION}}
    just install
    just lint
    just pre

# Show available commands
help:
    @just --list
