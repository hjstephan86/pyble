"""
conftest.py – pytest-Fixtures für Playwright UI-Tests.

Startet den FastAPI-Server einmalig pro Test-Session mit Coverage-Messung
und stellt eine live_server_url-Fixture bereit.
"""

import os
import subprocess
import sys
import time
import socket

import pytest
import requests


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_server(url: str, timeout: int = 40) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code < 500:
                return True
        except requests.ConnectionError:
            pass
        time.sleep(0.5)
    return False


@pytest.fixture(scope="session")
def live_server_url():
    """
    Startet uvicorn mit der pyble-App (optional mit Coverage) und
    gibt die Base-URL zurück. Der Prozess wird am Session-Ende beendet.
    """
    port = _find_free_port()

    # conftest.py liegt im Projektstamm (pyble/), src/ ist ein direktes Unterverzeichnis
    project_dir = os.path.abspath(os.path.dirname(__file__))
    src_dir     = os.path.join(project_dir, "src")

    env = os.environ.copy()
    env["PYTHONPATH"] = src_dir

    # Sicherstellen, dass Windows-Pflicht-Variablen vorhanden sind
    # (fehlen manchmal in eingeschränkten Umgebungen wie VS Code-Terminal)
    for var in ("SystemRoot", "ComSpec", "SYSTEMROOT"):
        if var not in env:
            default = r"C:\Windows" if "Root" in var else r"C:\Windows\System32\cmd.exe"
            env[var] = os.environ.get(var, default)

    # Direkt uvicorn starten (coverage run ist mit Python 3.14 noch nicht stabil)
    cmd = [
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", "127.0.0.1",
        "--port", str(port),
        "--log-level", "error",
    ]
    proc = subprocess.Popen(
        cmd,
        cwd=src_dir,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    base_url = f"http://127.0.0.1:{port}"
    if not _wait_for_server(f"{base_url}/api/translations", timeout=40):
        proc.kill()
        pytest.fail("FastAPI-Server hat sich nicht rechtzeitig gemeldet.")

    yield base_url

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
