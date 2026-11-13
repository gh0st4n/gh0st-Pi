"""
Error handling and recovery tests.
Run:
  uv run pytest tests/test_error_handling.py -v
"""
import pytest

pytestmark = pytest.mark.unit


class TestErrorModels:
    def test_error_types(self):
        from hexstrike.error_handling.models import ErrorType

        assert ErrorType.TIMEOUT.value == "timeout"
        assert ErrorType.PERMISSION_DENIED.value == "permission_denied"
        assert ErrorType.RATE_LIMITED.value == "rate_limited"

    def test_recovery_actions(self):
        from hexstrike.error_handling.models import RecoveryAction

        assert RecoveryAction.RETRY_WITH_BACKOFF.value == "retry_with_backoff"
        assert RecoveryAction.ADJUST_PARAMETERS.value == "adjust_parameters"


class TestErrorHandler:
    def test_classify_timeout(self):
        from hexstrike.error_handling.handler import IntelligentErrorHandler
        from hexstrike.error_handling.models import ErrorType

        handler = IntelligentErrorHandler()
        assert handler.classify_error("operation timed out") == ErrorType.TIMEOUT
        assert handler.classify_error("timeout", TimeoutError("timeout")) == ErrorType.TIMEOUT

    def test_classify_permission_denied(self):
        from hexstrike.error_handling.handler import IntelligentErrorHandler
        from hexstrike.error_handling.models import ErrorType

        handler = IntelligentErrorHandler()
        assert handler.classify_error("permission denied") == ErrorType.PERMISSION_DENIED

    def test_classify_tool_not_found(self):
        from hexstrike.error_handling.handler import IntelligentErrorHandler
        from hexstrike.error_handling.models import ErrorType

        handler = IntelligentErrorHandler()
        assert handler.classify_error("command not found") == ErrorType.TOOL_NOT_FOUND

    def test_handle_tool_failure_returns_strategy(self):
        from hexstrike.error_handling.handler import IntelligentErrorHandler

        handler = IntelligentErrorHandler()
        strategy = handler.handle_tool_failure(
            "nmap",
            TimeoutError("simulated timeout"),
            {"target": "127.0.0.1", "parameters": {}, "attempt_count": 1},
        )

        assert strategy is not None
        assert hasattr(strategy, "action")
        assert hasattr(strategy, "parameters")

    def test_get_alternative_tool_supports_context_or_legacy(self):
        from hexstrike.error_handling.handler import IntelligentErrorHandler

        handler = IntelligentErrorHandler()

        try:
            alternative = handler.get_alternative_tool("nmap", {})
        except TypeError:
            alternative = handler.get_alternative_tool("nmap")

        assert alternative in {"rustscan", "masscan", "zmap"}

    def test_required_methods_for_recovery_exist(self):
        """
        Recovery module membutuhkan method-method ini.
        Kalau test ini gagal, berarti handler.py masih versi terlalu sederhana.
        """
        from hexstrike.error_handling.handler import IntelligentErrorHandler

        handler = IntelligentErrorHandler()

        assert hasattr(handler, "auto_adjust_parameters")
        assert hasattr(handler, "_get_system_resources")
        assert hasattr(handler, "escalate_to_human")


class TestDegradation:
    def test_fallback_chain_excludes_failed_tools(self):
        from hexstrike.error_handling.degradation import GracefulDegradation

        manager = GracefulDegradation()
        chain = manager.create_fallback_chain("network_discovery", failed_tools=["nmap"])

        assert isinstance(chain, list)
        assert "nmap" not in chain
        assert len(chain) > 0

    def test_critical_operations(self):
        from hexstrike.error_handling.degradation import GracefulDegradation

        manager = GracefulDegradation()
        assert manager.is_critical_operation("network_discovery") is True
        assert manager.is_critical_operation("unknown_operation") is False

    def test_partial_failure_adds_degradation_info(self):
        from hexstrike.error_handling.degradation import GracefulDegradation

        manager = GracefulDegradation()
        result = manager.handle_partial_failure(
            "unknown_operation",
            {"success": False, "target": "127.0.0.1"},
            ["dummy_tool"],
        )

        assert "degradation_info" in result
        assert result["degradation_info"]["fallback_applied"] is True
        assert "manual_recommendations" in result


class TestRecovery:
    def test_execute_command_with_recovery_success(self, monkeypatch):
        import hexstrike.error_handling.recovery as recovery

        def fake_execute_command(command, use_cache=True):
            return {
                "success": True,
                "stdout": "ok",
                "stderr": "",
                "return_code": 0,
                "execution_time": 0.01,
            }

        monkeypatch.setattr(recovery, "execute_command", fake_execute_command)

        result = recovery.execute_command_with_recovery(
            "dummy",
            "echo ok",
            {"target": "127.0.0.1"},
            max_attempts=1,
        )

        assert result["success"] is True
        assert result["recovery_info"]["attempts_made"] == 1
        assert result["recovery_info"]["recovery_applied"] is False

    def test_execute_command_with_retry_then_success(self, monkeypatch):
        import hexstrike.error_handling.recovery as recovery

        calls = {"count": 0}

        def fake_execute_command(command, use_cache=True):
            calls["count"] += 1
            if calls["count"] == 1:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": "timeout",
                    "return_code": -1,
                }
            return {
                "success": True,
                "stdout": "ok",
                "stderr": "",
                "return_code": 0,
            }

        monkeypatch.setattr(recovery, "execute_command", fake_execute_command)
        monkeypatch.setattr(recovery.time, "sleep", lambda seconds: None)

        result = recovery.execute_command_with_recovery(
            "nmap",
            "nmap 127.0.0.1",
            {"target": "127.0.0.1"},
            max_attempts=2,
        )

        assert result["success"] is True
        assert result["recovery_info"]["attempts_made"] == 2
        assert result["recovery_info"]["recovery_applied"] is True
