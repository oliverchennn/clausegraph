"""Synthetic evidence preparation, including a genuinely image-only PDF."""
import importlib.util
from pathlib import Path
import json

import pytest
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("prepare_demo", ROOT / "scripts/prepare_extraction_demo.py")
prepare_demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare_demo)


def test_native_and_scanned_sources_have_explicit_expected_fields(tmp_path):
    native, scanned, expected = prepare_demo.prepare(tmp_path)
    assert "SYNTHETIC EVIDENCE ONLY" in native.read_text()
    assert "$123.45" in native.read_text()
    assert "September 28, 2026" in native.read_text()
    data = json.loads(expected.read_text())
    assert data["amount_cents"] == 12345 and data["due_date"] == "2026-09-28"
    reader = PdfReader(scanned)
    assert len(reader.pages) == 1 and not reader.pages[0].extract_text().strip()
    assert len(reader.pages[0].images) == 1
    before = native.read_bytes()
    with pytest.raises(FileExistsError):
        prepare_demo.prepare(tmp_path)
    assert native.read_bytes() == before
