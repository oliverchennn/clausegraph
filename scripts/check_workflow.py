"""Read-only lane, ancestry and conflict-marker checks, using the base's policy.

Patterns use fnmatchcase: '*' includes directory separators. First match wins.
Local pre-push fetches main in the hook, then calls this script for each pushed SHA.
"""
from __future__ import annotations

import argparse
from fnmatch import fnmatchcase
import json
from pathlib import Path
import re
import subprocess
import sys

POLICY = ".github/ownership.json"
MARKER = re.compile(rb"^(?:<{7} |={7}\r?$|>{7} |\|{7} )", re.MULTILINE)


def git(*args: str, cwd: str | Path | None = None) -> bytes:
    # Trust only this explicitly selected checkout, never all repositories.
    directory = str(Path(cwd or Path.cwd()).resolve()).replace("\\", "/")
    return subprocess.check_output(["git", "-c", f"safe.directory={directory}", *args], cwd=cwd)


def lane_for(branch: str) -> str:
    match = re.fullmatch(r"codex/(dev-[ab])/[a-z0-9][a-z0-9-]*", branch)
    if not match:
        raise ValueError("Use a fresh codex/dev-a/<task> or codex/dev-b/<task> branch.")
    return match[1]


def owner_for(path: str, policy: dict) -> str | None:
    return next((rule["owner"] for rule in policy["rules"]
                 if any(fnmatchcase(path, pattern) for pattern in rule["patterns"])), None)


def changed_paths(raw: bytes) -> list[str]:
    """Parse -z --name-status; include old and new names of renames/copies."""
    fields = raw.decode("utf-8").split("\0")
    paths = []
    index = 0
    while index < len(fields) and fields[index]:
        status = fields[index]
        count = 2 if status[0] in "RC" else 1
        paths.extend(fields[index + 1:index + 1 + count])
        index += count + 1
    return sorted(set(paths))


def ownership_errors(paths: list[str], lane: str, policy: dict) -> list[str]:
    return [f"{path}: owned by {owner_for(path, policy) or 'nobody (assign before editing)'}, not {lane}"
            for path in paths if owner_for(path, policy) != lane]


def check(base: str, head: str, branch: str, *, policy_file: str | None = None,
          require_current: bool = False) -> list[str]:
    lane = lane_for(branch)
    # Callers must explicitly provide a policy only during the initial bootstrap.
    policy = json.loads(Path(policy_file).read_text(encoding="utf-8") if policy_file
                        else git("show", f"{base}:{POLICY}"))
    errors = []
    if require_current:
        ancestor = git("merge-base", base, head).decode().strip()
        if ancestor != git("rev-parse", base).decode().strip():
            errors.append("Branch is behind main. Merge freshly fetched origin/main, resolve and rerun checks.")
    paths = changed_paths(git("diff", "--name-status", "-z", "--find-renames", f"{base}...{head}"))
    errors.extend(ownership_errors(paths, lane, policy))
    if paths and not any(path.startswith(f"docs/handoffs/{lane}/") and path.endswith(".md") for path in paths):
        errors.append(f"Include this task's own docs/handoffs/{lane}/<task>.md with exact checks and limitations.")
    existing = set(git("ls-tree", "-r", "--name-only", "-z", head).decode().split("\0"))
    for path in paths:
        if path not in existing:
            continue
        data = git("show", f"{head}:{path}")
        if b"\0" not in data and MARKER.search(data):
            errors.append(f"{path}: unresolved conflict marker")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--branch")
    parser.add_argument("--policy-file", help="Initial bootstrap only; normal checks always read base policy")
    parser.add_argument("--require-current", action="store_true")
    args = parser.parse_args()
    try:
        branch = args.branch or git("branch", "--show-current").decode().strip()
        errors = check(args.base, args.head, branch, policy_file=args.policy_file,
                       require_current=args.require_current)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Workflow check failed: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Workflow checks passed (lane ownership, task handoff, conflict markers" +
          (", current main)." if args.require_current else ")."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
