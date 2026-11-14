import json
from pathlib import Path
from typing import Any

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> Any:
    """Return the parsed JSON of ``test/fixtures/<name>.json``."""
    return json.loads((FIXTURES_DIR / f"{name}.json").read_text(encoding="utf-8"))
