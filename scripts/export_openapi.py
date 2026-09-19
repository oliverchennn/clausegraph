"""Export stable canonical OpenAPI. Run from repository root."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))


def export():
    try:
        from clausegraph.api import app
    except ModuleNotFoundError as exc:
        if exc.name != "clausegraph.api":
            raise
        from fastapi import FastAPI
        from clausegraph.schemas import Workspace, PlanRequest, PlanResult, IntakeRequest, RuleReview, UploadResponse, DraftResponse
        app = FastAPI(title="ClauseGraph", version="0.1.0")
        @app.get("/api/workspace", response_model=Workspace)
        def workspace(): ...
        @app.post("/api/plan", response_model=PlanResult)
        def plan(request: PlanRequest): ...
        @app.post("/api/intake", response_model=Workspace)
        def intake(request: IntakeRequest): ...
        @app.patch("/api/rules/{rule_id}", response_model=Workspace)
        def review(rule_id: str, request: RuleReview): ...
        @app.post("/api/documents", response_model=UploadResponse)
        def upload(): ...
        @app.post("/api/actions/{action_id}/draft", response_model=DraftResponse)
        def draft(action_id: str): ...
    path = ROOT / "docs" / "openapi.json"
    path.write_text(json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Exported {path}")


if __name__ == "__main__":
    export()
