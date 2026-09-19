"""Export stable canonical OpenAPI. Run from repository root."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))


def export():
    from clausegraph.api import app
    path = ROOT / "docs" / "openapi.json"
    path.write_text(json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Exported {path}")


if __name__ == "__main__":
    export()
