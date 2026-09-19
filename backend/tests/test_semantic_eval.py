import importlib.util
from pathlib import Path

import pytest

from clausegraph.config import Settings
from clausegraph.providers import ProviderError, Providers


def module():
    path = Path(__file__).resolve().parents[2] / "scripts/eval_nemotron.py"
    spec = importlib.util.spec_from_file_location("eval_nemotron", path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_eval_distinguishes_fixture_accuracy_and_rejected_hallucinations():
    report = module().evaluate()
    assert report["mode"] == "synthetic_fixture_gate_eval"
    assert not report["model_accuracy_measured"]
    assert report["case_count"] == 5
    assert report["structured_exact_count"] == 3
    assert report["citation_literal_valid_count"] == 3
    assert report["unreviewed_withheld_count"] == 5
    assert all(row["expected_gate_result"] for row in report["cases"])


def test_live_eval_without_key_never_falls_back_to_fixtures():
    with pytest.raises(ProviderError, match="no fixture fallback"):
        module().evaluate(live=True, provider=Providers(Settings(_env_file=None, nvidia_api_key="")))
