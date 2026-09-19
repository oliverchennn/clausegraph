"""Governance regressions: path ownership, renames and trusted-base policy."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("workflow", ROOT / "scripts/check_workflow.py")
workflow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow)
POLICY = json.loads((ROOT / ".github/ownership.json").read_text())


@pytest.mark.parametrize("path,owner", [
    ("backend/clausegraph/api.py", "dev-a"), ("frontend/src/app/page.tsx", "dev-b"),
    ("frontend/package-lock.json", "dev-a"), ("frontend/package.json", "dev-a"),
    ("frontend/src/lib/api-types.ts", "dev-a"), ("docs/DEMO.md", "dev-a"),
    ("docs/handoffs/dev-b/review-guidance.md", "dev-b"),
    ("docs/handoffs/dev-a/workflow.md", "dev-a"), ("unassigned.txt", None),
])
def test_ownership(path, owner):
    assert workflow.owner_for(path, POLICY) == owner
    if owner:
        assert not workflow.ownership_errors([path], owner, POLICY)
        assert workflow.ownership_errors([path], "dev-a" if owner == "dev-b" else "dev-b", POLICY)
    else:
        assert workflow.ownership_errors([path], "dev-a", POLICY)


def test_rename_checks_both_names():
    paths = workflow.changed_paths(b"R100\0docs/DEMO.md\0frontend/demo.md\0M\0frontend/src/app/page.tsx\0")
    assert paths == ["docs/DEMO.md", "frontend/demo.md", "frontend/src/app/page.tsx"]
    assert len(workflow.ownership_errors(paths, "dev-b", POLICY)) == 1


@pytest.mark.parametrize("branch", ["main", "codex/integration", "feature/test", "codex/dev-a/../bad"])
def test_reject_legacy_or_ambiguous_branch(branch):
    with pytest.raises(ValueError):
        workflow.lane_for(branch)


def test_marker_is_not_markdown_heading():
    assert workflow.MARKER.search(b"<<<<<<< HEAD\ntext\n=======\nother\n>>>>>>> main")
    assert not workflow.MARKER.search(b"# Heading\nordinary text\n")


def test_base_policy_cannot_be_relaxed_by_head(tmp_path, monkeypatch):
    def run(*args):
        return subprocess.check_output(["git", "-c", f"safe.directory={tmp_path.as_posix()}", *args], cwd=tmp_path)
    run("init", "-q")
    run("config", "user.email", "test@example.invalid")
    run("config", "user.name", "Workflow test")
    (tmp_path / ".github").mkdir()
    policy = tmp_path / workflow.POLICY
    policy.write_text(json.dumps(POLICY))
    run("add", ".")
    run("commit", "-qm", "base")
    base = run("rev-parse", "HEAD").decode().strip()
    policy.write_text(json.dumps({"rules": [{"patterns": ["*"], "owner": "dev-b"}]}))
    (tmp_path / "AGENTS.md").write_text("unauthorized")
    handoff = tmp_path / "docs/handoffs/dev-b/test.md"
    handoff.parent.mkdir(parents=True)
    handoff.write_text("test")
    run("add", ".")
    run("commit", "-qm", "attempt")
    monkeypatch.chdir(tmp_path)
    errors = workflow.check(base, "HEAD", "codex/dev-b/test", require_current=True)
    assert any("AGENTS.md: owned by dev-a" in error for error in errors)
    assert any("ownership.json: owned by dev-a" in error for error in errors)
    old_head = run("rev-parse", "HEAD").decode().strip()
    run("checkout", "--detach", base)
    (tmp_path / "README.md").write_text("main advanced")
    run("add", ".")
    run("commit", "-qm", "main change")
    errors = workflow.check("HEAD", old_head, "codex/dev-b/test", require_current=True)
    assert any("behind main" in error for error in errors)


def test_hook_installer_preserves_existing_and_rejects_custom_path(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setitem(sys.modules, "check_workflow", workflow)
    hook_spec = importlib.util.spec_from_file_location("installer", ROOT / "scripts/install_hooks.py")
    installer = importlib.util.module_from_spec(hook_spec)
    hook_spec.loader.exec_module(installer)
    hook = tmp_path / ".git/hooks/pre-push"
    original = "#!/bin/sh\necho prior-check\n"
    hook.write_text(original)
    assert installer.install() == hook
    assert hook.with_name("pre-push.clausegraph-previous").read_text() == original
    wrapped = hook.read_text()
    assert "pre-push.clausegraph.py" in wrapped
    assert hook.with_name("pre-push.clausegraph.py").read_bytes() == (ROOT / "scripts/pre_push.py").read_bytes()
    assert installer.install() == hook  # idempotent, backup unchanged
    assert hook.read_text() == wrapped
    workflow.git("config", "core.hooksPath", ".custom-hooks")
    with pytest.raises(RuntimeError, match="core.hooksPath"):
        installer.install()
    assert hook.read_text() == wrapped


def test_hook_runs_actual_local_push_preserving_input_and_rejecting_cross_lane(tmp_path, monkeypatch):
    remote = tmp_path / "remote.git"
    local = tmp_path / "local"
    subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(local)], check=True)
    monkeypatch.chdir(local)
    workflow.git("config", "user.email", "test@example.invalid")
    workflow.git("config", "user.name", "Workflow test")
    workflow.git("remote", "add", "origin", remote.as_posix())
    for name, content in [(workflow.POLICY, json.dumps(POLICY)),
                          ("scripts/check_workflow.py", (ROOT / "scripts/check_workflow.py").read_text())]:
        target = local / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    workflow.git("add", ".")
    workflow.git("commit", "-qm", "main policy")
    workflow.git("push", "-u", "origin", "main")
    workflow.git("checkout", "-b", "codex/dev-b/hook-test")
    (local / "frontend").mkdir()
    (local / "frontend/test.ts").write_text("export {}")
    handoff = local / "docs/handoffs/dev-b/hook-test.md"
    handoff.parent.mkdir(parents=True)
    handoff.write_text("hook test")
    workflow.git("add", ".")
    workflow.git("commit", "-qm", "frontend change")
    hook = local / ".git/hooks/pre-push"
    hook.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > .git/prior-args\nwhile read -r line; do printf "%s\\n" "$line"; done > .git/prior-input\n', newline="\n")
    os.chmod(hook, 0o755)
    monkeypatch.setitem(sys.modules, "check_workflow", workflow)
    hook_spec = importlib.util.spec_from_file_location("installer", ROOT / "scripts/install_hooks.py")
    installer = importlib.util.module_from_spec(hook_spec)
    hook_spec.loader.exec_module(installer)
    installer.install()
    workflow.git("push", "-u", "origin", "HEAD")
    assert (local / ".git/prior-args").read_text().splitlines()[0] == "origin"
    assert "refs/heads/codex/dev-b/hook-test" in (local / ".git/prior-input").read_text()
    (local / "AGENTS.md").write_text("cross-lane change")
    workflow.git("add", ".")
    workflow.git("commit", "-qm", "invalid")
    with pytest.raises(subprocess.CalledProcessError):
        workflow.git("push", "origin", "HEAD")
