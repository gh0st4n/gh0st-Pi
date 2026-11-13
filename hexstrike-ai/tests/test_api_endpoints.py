"""
API endpoint tests using Flask test_client.
Tidak menjalankan tool eksternal sungguhan; executor di-mock.

Run:
  uv run pytest tests/test_api_endpoints.py -v
"""
import importlib
import uuid
import pytest

pytestmark = pytest.mark.integration


def fake_execute_command(command, use_cache=True, *args, **kwargs):
    return {
        "success": True,
        "stdout": f"MOCK_EXECUTED: {command}",
        "stderr": "",
        "return_code": 0,
        "execution_time": 0.01,
        "timed_out": False,
        "partial_results": False,
    }


def fake_execute_with_recovery(tool_name, command, parameters=None, *args, **kwargs):
    result = fake_execute_command(command)
    result["recovery_info"] = {
        "attempts_made": 1,
        "recovery_applied": False,
        "recovery_history": [],
    }
    result["tool"] = tool_name
    return result


@pytest.fixture()
def app(monkeypatch):
    from hexstrike.api.app import create_app

    app = create_app(debug=True)
    app.config.update(TESTING=True)

    # Mock command execution in API modules so tests never run real tools.
    for module_name in [
        "hexstrike.api.health",
        "hexstrike.api.command",
        "hexstrike.api.tools_network",
        "hexstrike.api.tools_web",
        "hexstrike.api.tools_binary",
        "hexstrike.api.tools_cloud",
        "hexstrike.api.tools_forensics",
    ]:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue

        if hasattr(module, "execute_command"):
            monkeypatch.setattr(module, "execute_command", fake_execute_command)

        if hasattr(module, "execute_command_with_recovery"):
            monkeypatch.setattr(module, "execute_command_with_recovery", fake_execute_with_recovery)

        if hasattr(module, "telemetry"):
            monkeypatch.setattr(
                module.telemetry,
                "get_stats",
                lambda: {
                    "uptime_seconds": 1,
                    "commands_executed": 0,
                    "success_rate": "0.0%",
                    "average_execution_time": "0.00s",
                    "system_metrics": {},
                },
            )

    # Avoid DNS/network during intelligence tests.
    try:
        from hexstrike.intelligence.decision_engine import decision_engine

        monkeypatch.setattr(decision_engine, "_resolve_domain", lambda target: ["127.0.0.1"])
        monkeypatch.setattr(
            decision_engine,
            "optimize_parameters",
            lambda tool, profile, context=None: {"target": profile.target},
        )
    except Exception:
        pass

    return app


@pytest.fixture()
def client(app):
    return app.test_client()


def assert_ok(response):
    assert response.status_code == 200, response.get_data(as_text=True)
    data = response.get_json()
    assert isinstance(data, dict)
    return data


class TestBasicAPI:
    def test_health(self, client):
        data = assert_ok(client.get("/health"))
        assert data["status"] == "healthy"
        assert "version" in data

    def test_command(self, client):
        data = assert_ok(
            client.post(
                "/api/command",
                json={"command": "echo hello", "use_cache": False},
            )
        )
        assert data["success"] is True
        assert "MOCK_EXECUTED" in data["stdout"]

    def test_command_requires_command(self, client):
        response = client.post("/api/command", json={})
        assert response.status_code == 400


class TestFileAPI:
    def test_file_lifecycle(self, client):
        filename = f"pytest_{uuid.uuid4().hex}.txt"

        created = assert_ok(
            client.post(
                "/api/files/create",
                json={"filename": filename, "content": "hello"},
            )
        )
        assert created["success"] is True

        listed = assert_ok(client.get("/api/files/list"))
        assert listed["success"] is True
        assert any(item["name"] == filename for item in listed["files"])

        deleted = assert_ok(
            client.delete(
                "/api/files/delete",
                json={"filename": filename},
            )
        )
        assert deleted["success"] is True

    def test_payload_generation(self, client):
        data = assert_ok(
            client.post(
                "/api/payloads/generate",
                json={
                    "type": "buffer",
                    "size": 16,
                    "pattern": "A",
                    "filename": f"payload_{uuid.uuid4().hex}.txt",
                },
            )
        )
        assert data["success"] is True
        assert data["payload_info"]["size"] == 16


class TestIntelligenceAPI:
    def test_analyze_target(self, client):
        data = assert_ok(
            client.post(
                "/api/intelligence/analyze-target",
                json={"target": "http://example.local"},
            )
        )
        assert data["success"] is True
        assert data["target_profile"]["target_type"] == "web_application"

    def test_select_tools(self, client):
        data = assert_ok(
            client.post(
                "/api/intelligence/select-tools",
                json={"target": "http://example.local", "objective": "quick"},
            )
        )
        assert data["success"] is True
        assert data["tool_count"] > 0

    def test_optimize_parameters(self, client):
        data = assert_ok(
            client.post(
                "/api/intelligence/optimize-parameters",
                json={"target": "http://example.local", "tool": "nmap"},
            )
        )
        assert data["success"] is True
        assert "optimized_parameters" in data

    def test_create_attack_chain(self, client):
        data = assert_ok(
            client.post(
                "/api/intelligence/create-attack-chain",
                json={"target": "http://example.local"},
            )
        )
        assert data["success"] is True
        assert "attack_chain" in data

    def test_technology_detection(self, client):
        data = assert_ok(
            client.post(
                "/api/intelligence/technology-detection",
                json={"target": "http://example.local"},
            )
        )
        assert data["success"] is True
        assert "detected_technologies" in data


class TestWorkflowAPI:
    def test_bugbounty_recon(self, client):
        data = assert_ok(
            client.post(
                "/api/bugbounty/reconnaissance-workflow",
                json={"domain": "example.local"},
            )
        )
        assert data["success"] is True
        assert data["workflow"]["target"] == "example.local"

    def test_bugbounty_vuln_hunting(self, client):
        data = assert_ok(
            client.post(
                "/api/bugbounty/vulnerability-hunting-workflow",
                json={"domain": "example.local"},
            )
        )
        assert data["success"] is True
        assert "priority_score" in data["workflow"]

    def test_ctf_workflow(self, client):
        data = assert_ok(
            client.post(
                "/api/ctf/create-challenge-workflow",
                json={
                    "name": "Web1",
                    "category": "web",
                    "difficulty": "easy",
                    "description": "SQL injection challenge",
                },
            )
        )
        assert data["success"] is True
        assert data["workflow"]["challenge"] == "Web1"

    def test_ctf_suggest_tools(self, client):
        data = assert_ok(
            client.post(
                "/api/ctf/suggest-tools",
                json={
                    "category": "web",
                    "description": "SQL injection in login form",
                },
            )
        )
        assert data["success"] is True
        assert "sqlmap" in data["suggested_tools"]


class TestErrorHandlingAPI:
    def test_statistics(self, client):
        data = assert_ok(client.get("/api/error-handling/statistics"))
        assert data["success"] is True
        assert "statistics" in data

    def test_recovery_simulation(self, client):
        data = assert_ok(
            client.post(
                "/api/error-handling/test-recovery",
                json={
                    "tool_name": "nmap",
                    "error_type": "timeout",
                    "target": "127.0.0.1",
                },
            )
        )
        assert data["success"] is True
        assert "recovery_strategy" in data

    def test_alternative_tools(self, client):
        data = assert_ok(client.get("/api/error-handling/alternative-tools?tool_name=nmap"))
        assert data["success"] is True
        assert data["has_alternatives"] is True


class TestVisualAPI:
    def test_vulnerability_card(self, client):
        data = assert_ok(
            client.post(
                "/api/visual/vulnerability-card",
                json={
                    "name": "Test Finding",
                    "severity": "high",
                    "description": "Dummy finding",
                },
            )
        )
        assert data["success"] is True
        assert "vulnerability_card" in data

    def test_summary_report(self, client):
        data = assert_ok(
            client.post(
                "/api/visual/summary-report",
                json={
                    "target": "example.local",
                    "tools_used": ["dummy"],
                    "execution_time": 1.2,
                    "vulnerabilities": [],
                },
            )
        )
        assert data["success"] is True
        assert "summary_report" in data

    def test_tool_output(self, client):
        data = assert_ok(
            client.post(
                "/api/visual/tool-output",
                json={
                    "tool": "dummy",
                    "output": "found example\nwarning example",
                    "success": True,
                },
            )
        )
        assert data["success"] is True
        assert "formatted_output" in data


class TestProcessAPI:
    def test_process_list(self, client):
        data = assert_ok(client.get("/api/processes/list"))
        assert data["success"] is True
        assert "active_processes" in data

    def test_process_dashboard(self, client):
        data = assert_ok(client.get("/api/processes/dashboard"))
        assert "total_processes" in data
        assert "visual_dashboard" in data


class TestToolAPIWithMocks:
    @pytest.mark.parametrize(
        "endpoint,payload",
        [
            ("/api/tools/nmap", {"target": "127.0.0.1", "use_recovery": False}),
            ("/api/tools/masscan", {"target": "127.0.0.1", "ports": "80", "rate": 1}),
            ("/api/tools/gobuster", {"url": "http://127.0.0.1", "use_recovery": False}),
            ("/api/tools/nuclei", {"target": "http://127.0.0.1", "use_recovery": False}),
            ("/api/tools/sqlmap", {"url": "http://127.0.0.1", "data": ""}),
        ],
    )
    def test_tool_endpoint_mocked(self, client, endpoint, payload):
        data = assert_ok(client.post(endpoint, json=payload))
        assert data["success"] is True
        assert "MOCK_EXECUTED" in data["stdout"]


class TestVulnIntelAPI:
    def test_attack_chains_local(self, client):
        data = assert_ok(
            client.post(
                "/api/vuln-intel/attack-chains",
                json={"target_software": "nginx", "attack_depth": 2},
            )
        )
        assert data["success"] is True
        assert "attack_chain_discovery" in data

    def test_threat_feeds_non_cve_indicator(self, client):
        data = assert_ok(
            client.post(
                "/api/vuln-intel/threat-feeds",
                json={"indicators": ["127.0.0.1"], "timeframe": "30d"},
            )
        )
        assert data["success"] is True
        assert "threat_intelligence" in data
