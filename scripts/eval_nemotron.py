"""Reproducible synthetic extraction eval; default mode makes no provider requests."""
import argparse
import json
import sys
import time
from datetime import date, datetime, timezone
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from clausegraph.config import Settings  # noqa: E402
from clausegraph.extraction import compile_rules, validate_extraction  # noqa: E402
from clausegraph.providers import ProviderError, Providers  # noqa: E402
from clausegraph.schemas import (  # noqa: E402
    Document, DocumentPage, Evidence, ExtractionResult, Rule, Scenario,
)


def score(case: dict, result: ExtractionResult, document: Document) -> dict:
    expected = case["expected"]
    exact = len(result.rules) == 1 and all(
        result.rules[0].model_dump(mode="json")[field] == value for field, value in expected.items()
    )
    checked = validate_extraction(result, document)
    citations_valid = bool(checked.rules) and all(rule.evidence_status == "supported" for rule in checked.rules)
    compiled = compile_rules(checked)
    withheld = not compiled.events and not compiled.actions
    return {
        "id": case["id"], "structured_fields_exact": exact,
        "citations_and_literals_valid": citations_valid,
        "unreviewed_execution_withheld": withheld,
        "review_states": [rule.review_status.value for rule in checked.rules],
        "evidence_states": [rule.evidence_status for rule in checked.rules],
        "warnings": checked.warnings,
    }


def evaluate(*, live: bool = False, provider: Providers | None = None) -> dict:
    corpus = json.loads((ROOT / "fixtures/evals/semantic-clauses.json").read_text(encoding="utf-8"))
    if live:
        provider = provider or Providers(Settings())
        if not provider.settings.text_configured:
            raise ProviderError("Text provider configuration missing; no live evaluation performed and no fixture fallback.")
    scenario = Scenario(id="synthetic-eval", title="Synthetic extraction evaluation", start_date=date(2026, 9, 1),
                        opening_balance_cents=0, events=[], actions=[])
    rows = []
    for case in corpus["cases"]:
        started = time.monotonic()
        content = case["text"]
        document = Document(id=case["id"], name=case["id"] + ".txt", media_type="text/plain",
                            sha256=sha256(content.encode()).hexdigest(), synthetic=True,
                            created_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
                            pages=[DocumentPage(page=1, text=content)])
        try:
            if live:
                result = provider.extract(document, scenario)
            else:
                result = ExtractionResult(rules=[Rule(
                    id=case["id"], title="Synthetic candidate", **case["fixture_candidate"],
                    evidence=[Evidence(document_id=document.id, page=1, char_start=0,
                                       char_end=len(content), quote=content)],
                )])
            row = score(case, result, document)
            if not live:
                row["expected_gate_result"] = all(
                    state == case["expected_evidence"] for state in row["evidence_states"]
                ) and row["unreviewed_execution_withheld"]
        except ProviderError as exc:
            row = {"id": case["id"], "error": str(exc), "structured_fields_exact": False,
                   "citations_and_literals_valid": False, "unreviewed_execution_withheld": True}
        row["runtime_seconds"] = round(time.monotonic() - started, 6)
        rows.append(row)
    return {
        "mode": "live_nemotron" if live else "synthetic_fixture_gate_eval",
        "provider": provider.text_name if live else None,
        "model": provider.settings.text_model if live else None,
        "model_accuracy_measured": live,
        "case_count": len(rows),
        "structured_exact_count": sum(row["structured_fields_exact"] for row in rows),
        "citation_literal_valid_count": sum(row["citations_and_literals_valid"] for row in rows),
        "unreviewed_withheld_count": sum(row["unreviewed_execution_withheld"] for row in rows),
        "cases": rows,
        "limitations": "Five native-text synthetic clauses. No OCR, model evidence-check accuracy, human review, or live end-to-end claim. Fixture mode includes two deliberately faulty outputs.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Send five synthetic clauses to the configured NVIDIA/Brev text model; consumes quota/compute.")
    parser.add_argument("--consent-external", action="store_true", help="Authorize external processing of synthetic evaluation text.")
    args = parser.parse_args()
    if args.live and not args.consent_external:
        parser.error("--live requires --consent-external")
    try:
        report = evaluate(live=args.live)
    except ProviderError as exc:
        print(json.dumps({"mode": "live_nemotron", "status": "UNAVAILABLE", "error": str(exc)}))
        return 2
    print(json.dumps(report, indent=2))
    if args.live:
        return int(any(not row["structured_fields_exact"] or not row["citations_and_literals_valid"] for row in report["cases"]))
    return int(not all(row["expected_gate_result"] for row in report["cases"]))


if __name__ == "__main__":
    raise SystemExit(main())
