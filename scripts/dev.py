"""Run the local API, worker and Next.js together; Ctrl+C stops only these children."""
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if npm is None or not (ROOT / "frontend" / "node_modules").exists():
        raise SystemExit("Install Node.js and run npm ci in frontend first.")
    env = {**os.environ, "PYTHONPATH": str(ROOT / "backend"), "NEXT_TELEMETRY_DISABLED": "1"}
    children = []
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    commands = [
        ([sys.executable, "-m", "uvicorn", "clausegraph.api:app", "--host", "127.0.0.1", "--port", "8000", "--no-access-log"], ROOT),
        ([sys.executable, "-m", "clausegraph.worker"], ROOT),
        ([npm, "run", "dev"], ROOT / "frontend"),
    ]
    try:
        for command, directory in commands:
            children.append(subprocess.Popen(command, cwd=directory, env=env, creationflags=flags,
                                             start_new_session=os.name != "nt"))
        print("ClauseGraph: http://localhost:3000 | API: http://127.0.0.1:8000/api/health", flush=True)
        while all(child.poll() is None for child in children):
            time.sleep(0.5)
        failed = next(child for child in children if child.poll() is not None)
        print(f"A service exited with code {failed.returncode}; stopping this local stack.", flush=True)
    except KeyboardInterrupt:
        print("Stopping the local stack.", flush=True)
    finally:
        for child in children:
            if child.poll() is None:
                if os.name == "nt":
                    subprocess.run(["taskkill", "/PID", str(child.pid), "/T", "/F"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   creationflags=subprocess.CREATE_NO_WINDOW, check=False)
                else:
                    os.killpg(child.pid, signal.SIGTERM)
        for child in children:
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()


if __name__ == "__main__":
    main()
