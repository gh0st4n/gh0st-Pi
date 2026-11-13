"""
End-to-end test.
Aman: hanya health, echo localhost, file temp, intelligence lokal, visual.

Run:
  uv run python tests/test_e2e.py

Atau:
  RUN_E2E=1 uv run pytest tests/test_e2e.py -v
"""
import os
import sys
import time
import socket
import subprocess
import tempfile
from pathlib import Path

import pytest
import requests

pytestmark = [pytest.mark.e2e, pytest.mark.integration]

ROOT_DIR = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="module")
def server_url():
    """
    E2E menjalankan server sungguhan.
    Default pytest biasa akan skip supaya tidak mengganggu unit test cepat.
    """
    if os.environ.get("RUN_E2E") != "1":
        pytest.skip("E2E skipped. Run with RUN_E2E=1 or execute this file directly.")

    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT_DIR) + os.pathsep + env.get("PYTHONPATH", "")
    env["HEXSTRIKE_PORT"] = str(port)
    env["HEXSTRIKE_HOST"] = "127.0.0.1"

    log_file = tempfile.TemporaryFile(mode="w+", encoding="utf-8")

    proc = subprocess.Popen(
        [sys.executable, str(ROOT_DIR / "hexstrike_server.py"), "--port", str(port)],
        cwd=str(ROOT_DIR),
        env=env,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        text=True,
    )

    deadline = time.time() + 30
    last_error = None

    while time.time() < deadline:
        if proc.poll() is not None:
            log_file.seek(0)
            logs = log_file.read()
            raise RuntimeError(f"Server exited early with code {proc.returncode}\n{logs}")

        try:
            response = requests.get(f"{base_url}/health", timeout=15)
            if response.status_code == 200:
                break
        except Exception as exc:
            last_error = exc

        time.sleep(0.5)
    else:
        proc.terminate()
        log_file.seek(0)
        logs = log_file.read()
        raise RuntimeError(f"Server did not become ready: {last_error}\n{logs}")

    yield base_url

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)

    log_file.close()


def test_e2e_health(server_url):
    response = requests.get(f"{server_url}/health", timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_e2e_command_echo(server_url):
    response = requests.post(
        f"{server_url}/api/command",
        json={"command": "echo hexstrike_e2e_ok", "use_cache": False},
        timeout=10,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "hexstrike_e2e_ok" in data["stdout"]


def test_e2e_file_lifecycle(server_url):
    filename = f"e2e_{int(time.time())}.txt"

    created = requests.post(
        f"{server_url}/api/files/create",
        json={"filename": filename, "content": "hello-e2e"},
        timeout=10,
    )
    assert created.status_code == 200
    assert created.json()["success"] is True

    listed = requests.get(f"{server_url}/api/files/list", timeout=10)
    assert listed.status_code == 200
    assert any(item["name"] == filename for item in listed.json()["files"])

    deleted = requests.delete(
        f"{server_url}/api/files/delete",
        json={"filename": filename},
        timeout=10,
    )
    assert deleted.status_code == 200
    assert deleted.json()["success"] is True


def test_e2e_intelligence_local(server_url):
    response = requests.post(
        f"{server_url}/api/intelligence/analyze-target",
        json={"target": "http://127.0.0.1:9"},
        timeout=10,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["target_profile"]["target_type"] == "web_application"


def test_e2e_visual_card(server_url):
    response = requests.post(
        f"{server_url}/api/visual/vulnerability-card",
        json={
            "name": "E2E Finding",
            "severity": "info",
            "description": "Safe test finding",
        },
        timeout=10,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "vulnerability_card" in data


def test_e2e_error_statistics(server_url):
    response = requests.get(f"{server_url}/api/error-handling/statistics", timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "statistics" in data


if __name__ == "__main__":
    os.environ.setdefault("RUN_E2E", "1")
    raise SystemExit(pytest.main([__file__, "-v"]))
