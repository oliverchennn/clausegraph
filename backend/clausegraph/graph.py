"""Typed evidence/dependency graph. Source strings are always inert labels."""
from __future__ import annotations

from collections import defaultdict
from itertools import combinations

import networkx as nx

from .schemas import (
    DependencyGraph,
    Document,
    GraphEdge,
    GraphIssue,
    GraphNode,
    Rule,
    Scenario,
)


def _has_cycle(graph: nx.DiGraph, component: set[str]) -> bool:
    """Return True when a strongly connected component represents a cycle."""
    return len(component) > 1 or any(
        graph.has_edge(node, node) for node in component
    )


def dependency_issues(scenario: Scenario, rules: list[Rule]) -> list[GraphIssue]:
    """Return review blockers without guessing at ambiguous entity identities."""
    issues: list[GraphIssue] = []

    rule_map = {rule.id: rule for rule in rules}
    action_map = {action.id: action for action in scenario.actions}

    for label, values in (
        ("rule", rules),
        ("action", scenario.actions),
        ("event", scenario.events),
    ):
        ids = [value.id for value in values]

        if len(ids) != len(set(ids)):
            issues.append(
                GraphIssue(
                    code="duplicate_id",
                    message=f"Duplicate {label} identifiers are ambiguous.",
                    rule_ids=list(rule_map),
                )
            )

    for relation in ("dependencies", "supersedes"):
        graph = nx.DiGraph()
        graph.add_nodes_from(rule_map)

        for rule in rules:
            for target in getattr(rule, relation):
                if target not in rule_map:
                    issues.append(
                        GraphIssue(
                            code="missing_rule",
                            message=(
                                f"{rule.title} references missing rule {target}."
                            ),
                            rule_ids=[rule.id],
                        )
                    )
                else:
                    graph.add_edge(rule.id, target)

        for component in nx.strongly_connected_components(graph):
            if _has_cycle(graph, component):
                issues.append(
                    GraphIssue(
                        code="rule_cycle",
                        message=(
                            f"Unsupported {relation} cycle requires review."
                        ),
                        rule_ids=sorted(component),
                    )
                )

    action_graph = nx.DiGraph()
    action_graph.add_nodes_from(action_map)

    for action in scenario.actions:
        for target in action.requires:
            if target not in action_map:
                issues.append(
                    GraphIssue(
                        code="missing_action",
                        message=(
                            f"{action.title} requires missing action {target}."
                        ),
                        rule_ids=action.source_rule_ids,
                    )
                )
            else:
                action_graph.add_edge(action.id, target)

        for target in action.excludes:
            if target not in action_map:
                issues.append(
                    GraphIssue(
                        code="missing_action",
                        message=(
                            f"{action.title} excludes missing action {target}."
                        ),
                        rule_ids=action.source_rule_ids,
                    )
                )

        overlap = set(action.requires) & set(action.excludes)

        if overlap:
            issues.append(
                GraphIssue(
                    code="contradictory_dependency",
                    message=(
                        f"{action.title} both requires and excludes "
                        f"{', '.join(sorted(overlap))}."
                    ),
                    rule_ids=action.source_rule_ids,
                )
            )

    for component in nx.strongly_connected_components(action_graph):
        if _has_cycle(action_graph, component):
            affected = sorted(
                {
                    rule_id
                    for action_id in component
                    for rule_id in action_map[action_id].source_rule_ids
                }
            )

            issues.append(
                GraphIssue(
                    code="action_cycle",
                    message=(
                        "Unsupported action dependency cycle requires review."
                    ),
                    rule_ids=affected,
                )
            )

    groups: dict[tuple, list[Rule]] = defaultdict(list)

    for rule in rules:
        if rule.entity_ambiguous:
            issues.append(
                GraphIssue(
                    code="ambiguous_entity",
                    message=(
                        f"The party or account for {rule.title} "
                        "needs confirmation."
                    ),
                    rule_ids=[rule.id],
                )
            )

        if rule.evidence_status in ("disputed", "unsupported"):
            issues.append(
                GraphIssue(
                    code="unsupported_evidence",
                    message=(
                        f"Evidence for {rule.title} is {rule.evidence_status}."
                    ),
                    rule_ids=[rule.id],
                )
            )

        key = (
            rule.kind,
            " ".join(rule.title.casefold().split()),
            tuple(
                sorted(
                    party.casefold().strip()
                    for party in rule.parties
                )
            ),
        )

        if rule.review_status.value != "rejected":
            groups[key].append(rule)

    # Distinct labels cannot conceal disagreement about an explicitly linked obligation.
    for event in scenario.events:
        linked = [
            rule_map[rule_id]
            for rule_id in event.source_rule_ids
            if (
                rule_id in rule_map
                and rule_map[rule_id].kind == "obligation"
                and rule_map[rule_id].review_status.value != "rejected"
            )
        ]

        if len(linked) > 1:
            groups[("event", event.id)].extend(linked)

    obligations: dict[tuple[str, object], list] = defaultdict(list)

    for event in scenario.events:
        if event.direction == "expense" and event.obligation_id:
            obligations[(event.obligation_id, event.date)].append(event)

    for items in obligations.values():
        if len(items) > 1:
            issues.append(
                GraphIssue(
                    code="duplicate_obligation",
                    message=(
                        "Multiple ledger entries identify the same obligation "
                        "and due date; review is required before confirming a plan."
                    ),
                    rule_ids=sorted(
                        {
                            rule_id
                            for event in items
                            for rule_id in event.source_rule_ids
                        }
                    ),
                )
            )

    for group in groups.values():
        for left, right in combinations(group, 2):
            if left.id in right.supersedes or right.id in left.supersedes:
                continue

            amounts_conflict = (
                left.amount_cents is not None
                and right.amount_cents is not None
                and left.amount_cents != right.amount_cents
            )

            dates_conflict = (
                left.due_date is not None
                and right.due_date is not None
                and left.due_date != right.due_date
            )

            if amounts_conflict or dates_conflict:
                issues.append(
                    GraphIssue(
                        code="contradictory_clauses",
                        message=(
                            f"Conflicting amounts or dates for {left.title} "
                            "need explicit supersession or review."
                        ),
                        rule_ids=[left.id, right.id],
                    )
                )

    return issues