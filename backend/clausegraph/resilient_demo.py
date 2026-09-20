"""Separate human-authored synthetic fixture; never alters the original six sources."""
from datetime import date, datetime, timezone
from hashlib import sha256
from pathlib import Path

from .schemas import Action, Document, DocumentPage, Effect, Evidence, FinancialEvent, Rule, Scenario


def load_resilient_demo() -> tuple[Scenario, list[Document], list[Rule]]:
    directory = Path(__file__).resolve().parents[2] / "fixtures/resilient"
    if not directory.exists():
        directory = Path(__file__).resolve().parents[3] / "fixtures/resilient"
    # Synthetic originals are reconstructed from these canonical page strings.
    # Hash the same UTF-8 text across LF and Windows CRLF checkouts.
    documents = [Document(id=f"resilient-doc-{index}", name=path.name, sha256=sha256(text.encode("utf-8")).hexdigest(),
        media_type="text/plain", pages=[DocumentPage(page=1, text=text)],
        status="ready", synthetic=True, created_at=datetime(2026, 9, 1, tzinfo=timezone.utc))
        for index, path in enumerate(sorted(directory.glob("*.txt")), 1)
        for text in [path.read_text(encoding="utf-8")]]
    if len(documents) != 3:
        raise RuntimeError("The three separate resilient synthetic sources are required")

    def rule(identifier, title, doc, quote, **kwargs):
        document = documents[doc - 1]
        offset = document.pages[0].text.index(quote)
        return Rule(id=identifier, title=title, evidence=[Evidence(document_id=document.id, page=1,
            char_start=offset, char_end=offset + len(quote), quote=quote)],
            parties=["Alex Morgan"], review_status="reviewed", evidence_status="supported", extraction_confidence=1,
            verifier_notes="Human-authored synthetic fixture; no live model call.", **kwargs)

    rules = [
        rule("resilient-bill-rule", "Existing installment", 1,
             "Alex Morgan owes Clearpath Credit one installment of $100.00 on September 2, 2026.",
             kind="obligation", amount_cents=10000, due_date=date(2026, 9, 2)),
        rule("resilient-income-rule", "Expected paycheck", 2,
             "Juniper Studio expects to deposit a paycheck of $100.00 for Alex Morgan on September 3, 2026.",
             kind="obligation", amount_cents=10000, due_date=date(2026, 9, 3)),
    ]
    actions = []
    for name, day, fee, quote in [
        ("early", 3, 0, "APPROVED EARLY OPTION: Alex Morgan may move the $100.00 Clearpath Credit installment to September 3, 2026, with a $0.00 fee. Execute this option on September 1, 2026."),
        ("late", 5, 100, "APPROVED LATE OPTION: Alex Morgan may move the $100.00 Clearpath Credit installment to September 5, 2026, with a $1.00 fee charged on September 1, 2026. Execute this option on September 1, 2026."),
    ]:
        rid = f"resilient-{name}-rule"
        rules.append(rule(rid, f"Approved {name} payment option", 3, quote, kind="option", amount_cents=10000,
            due_date=date(2026, 9, day), dependencies=["resilient-bill-rule"], approval_status="approved"))
        actions.append(Action(id=f"{name}-shift", title=f"Move the installment to September {day}",
            description=f"Use the already-approved September {day} payment date for the same debt. This is timing relief, not savings.",
            kind="shift", source_rule_ids=[rid, "resilient-bill-rule"],
            effects=[Effect(operation="shift", target_event_id="resilient-bill", date=date(2026, 9, day))],
            earliest_date=date(2026, 9, 1), latest_date=date(2026, 9, 1), recommended_date=date(2026, 9, 1),
            excludes=["late-shift" if name == "early" else "early-shift"], fee_cents=fee,
            review_status="reviewed", approval_status="approved"))
    return Scenario(id="resilient-synthetic-7-days", title="Synthetic fixed-schedule alternative", start_date=date(2026, 9, 1),
        horizon_days=7, opening_balance_cents=5000, actions=actions, events=[
            FinancialEvent(id="resilient-bill", title="Existing installment", date=date(2026, 9, 2), amount_cents=10000,
                direction="expense", obligation_id="resilient-installment", source_rule_ids=["resilient-bill-rule"]),
            FinancialEvent(id="resilient-paycheck", title="Expected paycheck", date=date(2026, 9, 3), amount_cents=10000,
                direction="income", source_rule_ids=["resilient-income-rule"]),
        ]), documents, rules
