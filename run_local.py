"""
Run the full app from ONE terminal (no Docker).

The site opens at http://localhost:5173 — the browser only uses that address.
Vite proxies /api/* to the three backend services, so it feels like one website.

Prerequisites (once):
  cd planning-service && pip install -r requirements.txt
  cd operations-service && pip install -r requirements.txt
  cd analytics-service && pip install -r requirements.txt
  cd frontend && npm install

Then from project root:
  python run_local.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROCS: list[subprocess.Popen] = []


def start(
    cmd: list[str] | str,
    cwd: Path,
    env: dict[str, str] | None = None,
    *,
    shell: bool = False,
) -> subprocess.Popen:
    kw: dict = {"cwd": str(cwd)}
    if env is not None:
        kw["env"] = env
    if shell or isinstance(cmd, str):
        kw["shell"] = True
    p = subprocess.Popen(cmd, **kw)
    PROCS.append(p)
    return p


def shutdown() -> None:
    for p in PROCS:
        if p.poll() is None:
            p.terminate()
    for p in PROCS:
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
        except Exception:
            pass


def main() -> None:
    py = sys.executable

    print("Starting Planning API :8000 …")
    start([py, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"], ROOT / "planning-service")
    time.sleep(4)

    print("Starting Operations API :8001 …")
    env2 = {**os.environ, "PLANNING_SERVICE_URL": "http://127.0.0.1:8000"}
    start([py, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8001"], ROOT / "operations-service", env2)

    time.sleep(3)
    print("Starting Analytics API :8002 …")
    env3 = {
        **os.environ,
        "OPERATIONS_SERVICE_URL": "http://127.0.0.1:8001",
        "PLANNING_SERVICE_URL": "http://127.0.0.1:8000",
    }
    start([py, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8002"], ROOT / "analytics-service", env3)

    time.sleep(3)
    print("Starting website (Vite) :5173 …\n")
    if sys.platform == "win32":
        start("npm run dev", ROOT / "frontend", shell=True)
    else:
        start(["npm", "run", "dev"], ROOT / "frontend")

    print("=" * 60)
    print("  Open in your browser:  http://localhost:5173")
    print("  (One site — APIs are wired behind the scenes.)")
    print("  Press Ctrl+C here to stop everything.")
    print("=" * 60 + "\n")

    try:
        PROCS[-1].wait()
    except KeyboardInterrupt:
        print("\nStopping…")
    finally:
        shutdown()


if __name__ == "__main__":
    main()
