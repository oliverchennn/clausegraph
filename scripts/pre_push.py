"""Installed local hook runner; uses Python rather than optional shell utilities."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile


def main() -> None:
    payload = sys.stdin.buffer.read()
    previous = Path(__file__).with_name("pre-push.clausegraph-previous")
    if previous.is_file() and os.access(previous, os.X_OK):
        command = [str(previous), *sys.argv[1:]]
        if os.name == "nt":
            # Git for Windows runs shebang hooks through its own shell. Do the same,
            # without assuming Unix utilities have been added to the caller's PATH.
            git_exe = Path(shutil.which("git") or "git")
            shells = [git_exe.parent / "sh.exe", git_exe.parent.parent / "bin/sh.exe"]
            shell = next((str(path) for path in shells if path.exists()), shutil.which("sh"))
            if not shell:
                raise RuntimeError("Cannot locate Git's shell to preserve the existing hook.")
            command = [shell, "-c", 'exec "$@"', "clausegraph-previous", previous.as_posix(), *sys.argv[1:]]
        subprocess.run(command, input=payload, check=True)
    subprocess.run(["git", "fetch", "--no-tags", "origin", "main"], check=True)
    source = subprocess.check_output(["git", "show", "origin/main:scripts/check_workflow.py"])
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as stream:
        checker = Path(stream.name)
        stream.write(source)
    try:
        for line in payload.decode().splitlines():
            local_ref, local_sha, remote_ref, _ = line.split()
            if local_sha == "0" * 40:
                continue
            if local_ref == "HEAD":
                local_ref = subprocess.check_output(["git", "symbolic-ref", "--quiet", "HEAD"]).decode().strip()
            if not local_ref.startswith("refs/heads/") or local_ref != remote_ref:
                raise RuntimeError("Publish a named task branch under the same remote branch name.")
            subprocess.run([sys.executable, str(checker), "--base", "origin/main", "--head", local_sha,
                            "--branch", local_ref.removeprefix("refs/heads/"), "--require-current"], check=True)
    finally:
        checker.unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Pre-push failed: {exc}") from exc
