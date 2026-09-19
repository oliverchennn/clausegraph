"""Install a local pre-push wrapper without overwriting existing hook behavior."""
from __future__ import annotations

import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

from check_workflow import git

TAG = "# ClauseGraph workflow pre-push v1"


def install() -> Path:
    root = Path(git("rev-parse", "--show-toplevel").decode().strip())
    configured = subprocess.run(["git", "-c", f"safe.directory={root.as_posix()}",
                                 "config", "--path", "core.hooksPath"], cwd=root,
                                capture_output=True, text=True)
    # Avoid changing an external/global hooks directory or silently bypassing it.
    if configured.returncode == 0 and configured.stdout.strip():
        raise RuntimeError("core.hooksPath is already configured. Preserve it and chain the documented checker "
                           "from that hook, or review the configuration before using this installer.")
    hook = Path(git("rev-parse", "--git-path", "hooks/pre-push").decode().strip())
    if not hook.is_absolute():
        hook = root / hook
    if hook.is_symlink():
        raise RuntimeError("Existing pre-push is a symlink. Preserve it and chain the checker manually.")
    hook = hook.resolve()
    if hook.exists() and TAG in hook.read_text(encoding="utf-8", errors="replace"):
        return hook
    previous = hook.with_name("pre-push.clausegraph-previous")
    if previous.exists():
        raise RuntimeError(f"Existing backup {previous}; inspect it before installing. Nothing changed.")
    hook.parent.mkdir(parents=True, exist_ok=True)
    if hook.exists():
        shutil.copy2(hook, previous)
    python = shlex.quote(Path(sys.executable).as_posix())
    runner = hook.with_name("pre-push.clausegraph.py")
    runner.write_text(Path(__file__).with_name("pre_push.py").read_text(encoding="utf-8"),
                      encoding="utf-8", newline="\n")
    text = f'''#!/bin/sh
{TAG}
exec {python} {shlex.quote(runner.as_posix())} "$@"
'''
    hook.write_text(text, encoding="utf-8", newline="\n")
    os.chmod(hook, 0o755)
    return hook


if __name__ == "__main__":
    try:
        print(f"Installed workflow hook: {install()}")
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        raise SystemExit(str(exc)) from exc
