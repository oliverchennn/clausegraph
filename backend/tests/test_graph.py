from clausegraph.demo import load_demo
from clausegraph.graph import build_graph
from clausegraph.schemas import DependencyGraph


def test_demo_graph_is_typed_and_edges_retain_evidence_rule_ids():
    scenario, documents, rules = load_demo()
    graph = build_graph(scenario, rules, documents)
    assert isinstance(graph, DependencyGraph)
    assert {node.kind for node in graph.nodes} == {"document", "rule", "action", "event", "entity"}
    assert all(edge.rule_ids for edge in graph.edges)
    assert any(edge.relation == "triggers" and edge.target == "event:device" for edge in graph.edges)
    assert not graph.issues


def test_conflicting_clauses_require_explicit_supersession():
    scenario, documents, rules = load_demo()
    conflict = rules[0].model_copy(deep=True)
    conflict.id = "conflict"
    conflict.amount_cents = 170000
    graph = build_graph(scenario, rules + [conflict], documents)
    assert any(issue.code == "contradictory_clauses" for issue in graph.issues)
    conflict.supersedes = [rules[0].id]
    assert not any(issue.code == "contradictory_clauses" for issue in build_graph(scenario, rules + [conflict], documents).issues)


def test_cycles_ambiguous_entities_and_missing_references_are_visible():
    scenario, documents, rules = load_demo()
    rules[0].dependencies = [rules[1].id]
    rules[1].dependencies = [rules[0].id]
    rules[2].entity_ambiguous = True
    rules[3].dependencies = ["missing"]
    scenario.actions[0].requires = [scenario.actions[1].id]
    scenario.actions[1].requires = [scenario.actions[0].id]
    codes = {issue.code for issue in build_graph(scenario, rules, documents).issues}
    assert {"rule_cycle", "ambiguous_entity", "missing_rule", "action_cycle"} <= codes
