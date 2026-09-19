"""Six clearly synthetic sources and a reproducible 60-day scenario."""
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path

from .schemas import (
    Action, Condition, Document, DocumentPage, Effect, Evidence, FinancialEvent,
    Rule, Scenario,
)

START = date(2026, 9, 1)


def load_demo() -> tuple[Scenario, list[Document], list[Rule]]:
    fixture_dir = Path(__file__).resolve().parents[2] / "fixtures"
    if not fixture_dir.exists():
        fixture_dir = Path(__file__).resolve().parents[3] / "fixtures"
    documents = []
    for index, path in enumerate(sorted(fixture_dir.glob("0*.*")), 1):
        content = path.read_bytes()
        documents.append(Document(
            id=f"doc-{index}", name=path.name, sha256=sha256(content).hexdigest(),
            media_type="text/csv" if path.suffix == ".csv" else "text/plain",
            pages=[DocumentPage(page=1, text=content.decode("utf-8"))],
            status="ready", synthetic=True, created_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
        ))
    if len(documents) != 6:
        raise RuntimeError("The six synthetic fixture documents are required")

    def evidence(doc: int, quote: str) -> list[Evidence]:
        document = documents[doc - 1]
        offset = document.pages[0].text.index(quote)
        return [Evidence(document_id=document.id, page=1, char_start=offset,
                         char_end=offset + len(quote), quote=quote)]

    def rule(id: str, title: str, doc: int, quote: str, **kwargs) -> Rule:
        return Rule(id=id, title=title, evidence=evidence(doc, quote),
                    review_status="reviewed", evidence_status="supported",
                    extraction_confidence=1.0, verifier_notes="Human-authored synthetic fixture; no live model call.",
                    **kwargs)

    rules = [
        rule("rule-rent", "Protect housing", 1,
             "The rent payment of $1,600.00 is due September 8, 2026.",
             kind="obligation", amount_cents=160000, due_date=START + timedelta(days=7), parties=["Harbor House", "Alex Morgan"]),
        rule("rule-phone", "Phone service payment", 2,
             "The next mobile service payment is $60.00 on September 11, 2026.",
             kind="obligation", amount_cents=6000, due_date=START + timedelta(days=10), parties=["Northstar Mobile", "Alex Morgan"]),
        rule("rule-device", "Remaining device principal", 2,
             "The remaining device principal of $480.00 is due November 20, 2026.",
             kind="obligation", amount_cents=48000, due_date=START + timedelta(days=80), parties=["Northstar Mobile", "Alex Morgan"]),
        rule("rule-cancel", "Cancellation accelerates device balance", 2,
             "If mobile service is cancelled by September 10, 2026, the $60.00 service payment is removed, and the existing $480.00 device balance becomes due on the cancellation date.",
             kind="option", amount_cents=48000, dependencies=["rule-phone", "rule-device"], parties=["Northstar Mobile", "Alex Morgan"]),
        rule("rule-loan", "Installment payment", 3,
             "Your scheduled installment is $450.00 due September 13, 2026.",
             kind="obligation", amount_cents=45000, due_date=START + timedelta(days=12), parties=["Clearpath Credit", "Alex Morgan"]),
        rule("rule-shift", "Approved payment shift", 3,
             "APPROVED: You may move the $450.00 installment from September 13 to September 26, 2026, with a $0.00 fee. Confirm the change by September 12, 2026.",
             kind="option", amount_cents=45000, due_date=START + timedelta(days=25),
             approval_status="approved", dependencies=["rule-loan"], parties=["Clearpath Credit", "Alex Morgan"]),
        rule("rule-utilities", "Essential utilities", 4,
             "true,Utilities,2026-09-16,120.00,true,utilities", kind="obligation", amount_cents=12000,
             due_date=START + timedelta(days=15), parties=["Alex Morgan"]),
        rule("rule-groceries", "Essential groceries", 4,
             "true,Groceries,2026-09-19,170.00,true,food", kind="obligation", amount_cents=17000,
             due_date=START + timedelta(days=18), parties=["Alex Morgan"]),
        rule("rule-income", "Expected final paycheck", 5,
             "An expected final paycheck of $900.00 will be deposited September 21, 2026.",
             kind="obligation", amount_cents=90000, due_date=START + timedelta(days=20), parties=["Juniper Studio", "Alex Morgan"]),
        Rule(id="rule-assistance", title="Assistance eligibility unconfirmed", kind="benefit",
             evidence=evidence(6, "Applicants may request a one-time $300.00 emergency assistance grant. Payment depends on eligibility review and written approval. No eligibility decision, payment date, or approval has been issued for Alex Morgan."),
             parties=["Community Bridge", "Alex Morgan"], amount_cents=30000,
             conditions=[Condition(fact="eligibility_confirmed", operator="eq", value=True)],
             review_status="unresolved", approval_status="pending", evidence_status="supported",
             extraction_confidence=1, verifier_notes="Amount is described, but eligibility and payment date remain unresolved; excluded from all executable plans."),
    ]

    def event(id: str, title: str, day: int, amount: int, source: str, **kwargs) -> FinancialEvent:
        return FinancialEvent(id=id, title=title, date=START + timedelta(days=day), amount_cents=amount,
                              source_rule_ids=[source], obligation_id=id, **kwargs)

    events = [
        event("rent", "Rent", 7, 160000, "rule-rent", direction="expense", essential=True, service_id="housing"),
        event("phone", "Phone service", 10, 6000, "rule-phone", direction="expense", service_id="phone"),
        event("loan", "Installment", 12, 45000, "rule-loan", direction="expense"),
        event("utilities", "Utilities", 15, 12000, "rule-utilities", direction="expense", essential=True, service_id="utilities"),
        event("groceries", "Groceries", 18, 17000, "rule-groceries", direction="expense", essential=True, service_id="food"),
        event("paycheck", "Expected paycheck", 20, 90000, "rule-income", direction="income"),
        event("device", "Device principal", 80, 48000, "rule-device", direction="expense", service_id="phone"),
    ]
    actions = [
        Action(id="shift-payment", title="Move the $450 installment", description="Use the approved September 26 payment date. Confirm the change before September 12. This is a deferral, not savings.",
               kind="shift", source_rule_ids=["rule-shift", "rule-loan"],
               effects=[Effect(operation="shift", target_event_id="loan", date=START + timedelta(days=25))],
               earliest_date=START, latest_date=START + timedelta(days=11), recommended_date=START + timedelta(days=3),
               review_status="reviewed", approval_status="approved"),
        Action(id="cancel-phone", title="Cancel phone service", description="Removing the $60 service payment makes the existing $480 device debt due immediately, reducing cash by $420 within this horizon.",
               kind="cancel", source_rule_ids=["rule-cancel", "rule-device", "rule-phone"],
               effects=[Effect(operation="remove", target_event_id="phone"), Effect(operation="accelerate", target_event_id="device", offset_days=0)],
               earliest_date=START, latest_date=START + timedelta(days=9), recommended_date=START + timedelta(days=3),
               review_status="reviewed", approval_status="not_required", preserves_essential_services=False, service_id="phone"),
        Action(id="claim-assistance", title="Check emergency assistance eligibility", description="The guide describes a possible $300 grant, but eligibility, approval and payment timing are unresolved. No income is assumed.",
               kind="claim", source_rule_ids=["rule-assistance"], effects=[],
               earliest_date=START, latest_date=START + timedelta(days=59), recommended_date=START + timedelta(days=2),
               review_status="unresolved", approval_status="pending"),
    ]
    return Scenario(id="demo-60-days", title="Income interruption plan", start_date=START, horizon_days=60,
                    opening_balance_cents=200000, events=events, actions=actions,
                    essential_service_ids=["housing", "utilities", "food"]), documents, rules
