"""Canonical public contracts. Integration owner controls interface changes."""
from datetime import date as Date, datetime
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class ReviewStatus(str, Enum):
    pending = "pending"
    reviewed = "reviewed"
    rejected = "rejected"
    unresolved = "unresolved"


class ApprovalStatus(str, Enum):
    not_required = "not_required"
    pending = "pending"
    approved = "approved"
    denied = "denied"


class Evidence(Contract):
    document_id: str
    version: int = Field(default=1, ge=1)
    page: int = Field(ge=1)
    char_start: int = Field(ge=0)
    char_end: int = Field(ge=0)
    quote: str


class DocumentPage(Contract):
    page: int = Field(ge=1)
    text: str


class Document(Contract):
    id: str
    name: str
    media_type: str
    sha256: str
    version: int = 1
    pages: list[DocumentPage] = Field(default_factory=list)
    status: Literal["uploaded", "extracting", "needs_review", "ready", "failed"] = "uploaded"
    synthetic: bool = False
    created_at: datetime
    error: str | None = None


class Condition(Contract):
    fact: str
    operator: Literal["eq", "gte", "lte", "exists"] = "eq"
    value: str | int | bool | None = None
    resolved: bool = False
    satisfied: bool | None = None


class Rule(Contract):
    id: str
    title: str
    kind: Literal["obligation", "benefit", "option", "constraint"]
    evidence: list[Evidence]
    parties: list[str] = Field(default_factory=list)
    conditions: list[Condition] = Field(default_factory=list)
    amount_cents: Annotated[int | None, Field(default=None, ge=0, strict=True)]
    due_date: Date | None = None
    dependencies: list[str] = Field(default_factory=list)
    review_status: ReviewStatus = ReviewStatus.pending
    approval_status: ApprovalStatus = ApprovalStatus.not_required
    extraction_confidence: float = Field(default=0, ge=0, le=1)
    evidence_status: Literal["unchecked", "supported", "disputed", "unsupported"] = "unchecked"
    verifier_notes: str | None = None
    consequential: bool = True
    entity_ambiguous: bool = False
    supersedes: list[str] = Field(default_factory=list)


class FinancialEvent(Contract):
    id: str
    title: str
    date: Date
    amount_cents: Annotated[int, Field(ge=0, strict=True)]
    direction: Literal["income", "expense"]
    kind: Literal["actual", "projected"] = "projected"
    essential: bool = False
    service_id: str | None = None
    obligation_id: str | None = None
    source_rule_ids: list[str] = Field(default_factory=list)


class Effect(Contract):
    operation: Literal["shift", "remove", "add", "accelerate"]
    target_event_id: str | None = None
    event: FinancialEvent | None = None
    date: Date | None = None
    offset_days: int | None = None

    @model_validator(mode="after")
    def shape(self):
        if self.operation == "add" and self.event is None:
            raise ValueError("add requires an event")
        if self.operation != "add" and self.target_event_id is None:
            raise ValueError("event mutation requires target_event_id")
        if self.operation in ("shift", "accelerate") and self.date is None and self.offset_days is None:
            raise ValueError("date mutation requires date or execution offset")
        return self


class Action(Contract):
    id: str
    title: str
    description: str
    kind: Literal["shift", "cancel", "claim", "request", "keep"]
    source_rule_ids: list[str]
    effects: list[Effect] = Field(default_factory=list)
    earliest_date: Date
    latest_date: Date
    recommended_date: Date
    requires: list[str] = Field(default_factory=list)
    excludes: list[str] = Field(default_factory=list)
    approval_status: ApprovalStatus = ApprovalStatus.not_required
    review_status: ReviewStatus = ReviewStatus.pending
    preserves_essential_services: bool = True
    service_id: str | None = None
    fee_cents: Annotated[int, Field(default=0, ge=0, strict=True)]
    burden: int = Field(default=1, ge=0)


class GraphNode(Contract):
    id: str
    label: str
    kind: Literal["document", "rule", "action", "event", "entity"]
    reference_id: str
    status: str


class GraphEdge(Contract):
    id: str
    source: str
    target: str
    relation: Literal["requires", "triggers", "excludes", "supersedes", "supports"]
    rule_ids: list[str] = Field(default_factory=list)
    label: str | None = None


class GraphIssue(Contract):
    code: str
    message: str
    rule_ids: list[str] = Field(default_factory=list)
    blocking: bool = True


class DependencyGraph(Contract):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    issues: list[GraphIssue] = Field(default_factory=list)


class Scenario(Contract):
    id: str
    title: str
    start_date: Date
    horizon_days: int = Field(default=60, ge=1, le=366)
    opening_balance_cents: Annotated[int, Field(ge=0, le=10000000000, strict=True)]
    events: list[FinancialEvent]
    actions: list[Action]
    essential_service_ids: list[str] = Field(default_factory=list)


class PlanRequest(Contract):
    opening_balance_cents: Annotated[int | None, Field(default=None, ge=0, strict=True)]
    horizon_days: int | None = Field(default=None, ge=1, le=366)
    approval_overrides: dict[str, ApprovalStatus] = Field(default_factory=dict)
    action_dates: dict[str, Date] = Field(default_factory=dict)
    force_action_ids: list[str] = Field(default_factory=list)
    exclude_action_ids: list[str] = Field(default_factory=list)
    include_conditional: bool = False
    income_date: Date | None = None
    income_cents: Annotated[int | None, Field(default=None, ge=0, strict=True)]


class DailyBalance(Contract):
    date: Date
    balance_cents: int
    income_cents: int
    expense_cents: int
    event_ids: list[str] = Field(default_factory=list)


class Simulation(Contract):
    daily: list[DailyBalance]
    minimum_balance_cents: int
    ending_balance_cents: int
    first_shortfall_date: Date | None
    additional_cash_required_cents: int
    beyond_horizon: list[FinancialEvent] = Field(default_factory=list)


class PlannedAction(Contract):
    action_id: str
    execution_date: Date
    order: int
    explanation: str
    source_rule_ids: list[str]
    conditional: bool = False


class EventChange(Contract):
    operation: Literal["shift", "remove", "add", "accelerate", "fee"]
    before: FinancialEvent | None = None
    after: FinancialEvent | None = None


class DecisionTrace(Contract):
    action_id: str
    execution_date: Date
    source_rule_ids: list[str]
    source_document_ids: list[str]
    changes: list[EventChange] = Field(default_factory=list)


class PlanResult(Contract):
    id: str
    revision: int = 1
    state: Literal["confirmed", "conditional", "infeasible", "unresolved"]
    solver_status: Literal["OPTIMAL", "FEASIBLE", "INFEASIBLE", "UNKNOWN", "MODEL_INVALID"]
    solver_wall_time_seconds: float
    baseline: Simulation
    proposed: Simulation
    actions: list[PlannedAction]
    decision_traces: list[DecisionTrace] = Field(default_factory=list)
    excluded_actions: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    objective_proven: bool = False
    generated_at: datetime
    assumptions: PlanRequest = Field(default_factory=PlanRequest)


class UncertaintyBasis(Contract):
    id: str = Field(min_length=1, max_length=80)
    # The MVP deliberately accepts user declarations, not inferred source ranges.
    basis: Literal["user_assumption"] = "user_assumption"
    rationale: str = Field(min_length=1, max_length=1000)


class IncomeDateUncertainty(UncertaintyBasis):
    kind: Literal["income_date"] = "income_date"
    event_id: str
    earliest: Date
    latest: Date

    @model_validator(mode="after")
    def ordered(self):
        if self.latest < self.earliest:
            raise ValueError("Income date bounds must be ordered.")
        return self


class IncomeAmountUncertainty(UncertaintyBasis):
    kind: Literal["income_amount"] = "income_amount"
    event_id: str
    minimum_cents: Annotated[int, Field(ge=0, le=10000000000, strict=True)]
    maximum_cents: Annotated[int, Field(ge=0, le=10000000000, strict=True)]

    @model_validator(mode="after")
    def ordered(self):
        if self.maximum_cents < self.minimum_cents:
            raise ValueError("Income amount bounds must be ordered.")
        return self


class ApprovalUncertainty(UncertaintyBasis):
    kind: Literal["approval"] = "approval"
    target_id: str
    outcomes: list[Literal["approved", "denied", "pending"]] = Field(min_length=1, max_length=3)

    @model_validator(mode="after")
    def unique(self):
        if len(set(self.outcomes)) != len(self.outcomes):
            raise ValueError("Approval outcomes must be unique.")
        return self


Uncertainty = Annotated[IncomeDateUncertainty | IncomeAmountUncertainty | ApprovalUncertainty, Field(discriminator="kind")]


class VerificationRequest(Contract):
    plan_id: str
    revision: int = Field(ge=1)
    uncertainties: list[Uncertainty] = Field(default_factory=list, max_length=8)
    max_cases: int = Field(default=10000, ge=1, le=10000, strict=True)
    time_limit_seconds: float = Field(default=5, gt=0, le=10)

    @model_validator(mode="after")
    def unique_dimensions(self):
        if len({item.id for item in self.uncertainties}) != len(self.uncertainties):
            raise ValueError("Uncertainty dimension IDs must be unique.")
        targets = [(item.kind, getattr(item, "event_id", getattr(item, "target_id", None))) for item in self.uncertainties]
        if len(set(targets)) != len(targets):
            raise ValueError("Each uncertain property may be declared only once.")
        return self


class UncertaintyAssignment(Contract):
    dimension_id: str
    value: str | int


class VerificationFailure(Contract):
    property: Literal["nonnegative_balance", "authorization", "evidence", "accounting", "essential_services", "dependencies"]
    message: str
    date: Date | None = None
    action_id: str | None = None
    source_rule_ids: list[str] = Field(default_factory=list)


class VerificationTraceEvent(Contract):
    event: FinancialEvent
    action_ids: list[str] = Field(default_factory=list)


class Counterexample(Contract):
    assignment: list[UncertaintyAssignment]
    earliest_failing_date: Date | None = None
    balance_cents: int | None = None
    failures: list[VerificationFailure]
    simulation: Simulation | None = None
    events: list[VerificationTraceEvent] = Field(default_factory=list)


class VerificationResult(Contract):
    id: str
    plan_id: str
    revision: int
    mode: Literal["verify_fixed_plan"] = "verify_fixed_plan"
    status: Literal["SAFE", "UNSAFE", "UNKNOWN"]
    solver: Literal["exhaustive_finite_model_checker"] = "exhaustive_finite_model_checker"
    solver_status: Literal["EXHAUSTED", "TIME_LIMIT", "CASE_LIMIT", "INVALID_MODEL"]
    runtime_seconds: float
    horizon_start: Date
    horizon_end_exclusive: Date
    assumptions: VerificationRequest
    nominal_assumptions: PlanRequest
    fixed_actions: list[PlannedAction]
    dimension_count: int
    total_cases: int
    checked_cases: int
    coverage_complete: bool
    worst_case: Simulation | None = None
    worst_case_assignment: list[UncertaintyAssignment] = Field(default_factory=list)
    worst_case_proven: bool = False
    counterexample: Counterexample | None = None
    statement: str
    warnings: list[str] = Field(default_factory=list)
    generated_at: datetime


class JobStatus(Contract):
    id: str
    status: Literal["queued", "running", "completed", "failed"]
    stage: str
    progress: int = Field(ge=0, le=100)
    document_id: str | None = None
    error: str | None = None
    updated_at: datetime


class ProviderStatus(Contract):
    name: str
    configured: bool
    mode: Literal["live", "offline", "unavailable"]
    model: str | None = None
    detail: str


class Workspace(Contract):
    session_id: str
    mode: Literal["synthetic", "live"]
    revision: int
    scenario: Scenario
    documents: list[Document]
    rules: list[Rule]
    graph: DependencyGraph
    plan: PlanResult | None = None
    jobs: list[JobStatus] = Field(default_factory=list)
    providers: list[ProviderStatus] = Field(default_factory=list)


class RuleReview(Contract):
    review_status: ReviewStatus
    approval_status: ApprovalStatus | None = None
    amount_cents: Annotated[int | None, Field(default=None, ge=0, strict=True)]
    due_date: Date | None = None
    note: str | None = None
    conditions: list[Condition] | None = None
    evidence_confirmed: bool = False


class ExtractionResult(Contract):
    rules: list[Rule]
    actions: list[Action] = Field(default_factory=list)
    events: list[FinancialEvent] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class UploadResponse(Contract):
    document: Document
    job: JobStatus | None = None
    duplicate: bool = False


class IntakeRequest(Contract):
    opening_balance_cents: Annotated[int, Field(ge=0, strict=True)]
    start_date: Date
    horizon_days: int = Field(default=60, ge=1, le=366)
    events: list[FinancialEvent]
    essential_service_ids: list[str] = Field(default_factory=list)


class DraftResponse(Contract):
    action_id: str
    subject: str
    body: str
    sent: Literal[False] = False


class SessionCreate(Contract):
    demo: bool = False


class DraftRequest(Contract):
    use_provider: bool = False
    consent: bool = False


class AudioRequest(Contract):
    consent: bool = False


class TranscriptResponse(Contract):
    text: str
    facts_confirmed: Literal[False] = False


class DeleteResponse(Contract):
    deleted: bool


class HealthResponse(Contract):
    status: str
    database: str
    storage: str
