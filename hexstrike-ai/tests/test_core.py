"""
Core module tests.
Run:
  uv run pytest tests/test_core.py -v
"""
import time
import pytest

pytestmark = pytest.mark.unit


class TestColors:
    def test_colors_available(self):
        from hexstrike.core.colors import HexStrikeColors

        required = [
            "RED",
            "GREEN",
            "RESET",
            "BOLD",
            "SUCCESS",
            "WARNING",
            "ERROR",
            "CRITICAL",
            "HACKER_RED",
            "PRIMARY_BORDER",
            "ACCENT_LINE",
        ]

        for name in required:
            assert hasattr(HexStrikeColors, name), f"Missing color: {name}"
            assert isinstance(getattr(HexStrikeColors, name), str)


class TestCache:
    def test_hexstrike_cache_set_get(self):
        from hexstrike.core.cache import HexStrikeCache

        cache = HexStrikeCache(max_size=4, ttl=60)
        cache.set("echo test", {}, {"success": True, "stdout": "test"})

        result = cache.get("echo test", {})
        assert result is not None
        assert result["success"] is True
        assert result["stdout"] == "test"

    def test_hexstrike_cache_miss(self):
        from hexstrike.core.cache import HexStrikeCache

        cache = HexStrikeCache(max_size=4, ttl=60)
        assert cache.get("not-exists", {}) is None

    def test_hexstrike_cache_eviction(self):
        from hexstrike.core.cache import HexStrikeCache

        cache = HexStrikeCache(max_size=2, ttl=60)
        cache.set("cmd1", {}, {"id": 1})
        cache.set("cmd2", {}, {"id": 2})
        cache.set("cmd3", {}, {"id": 3})

        assert cache.get("cmd1", {}) is None
        assert cache.get("cmd2", {}) is not None
        assert cache.get("cmd3", {}) is not None

    def test_hexstrike_cache_stats(self):
        from hexstrike.core.cache import HexStrikeCache

        cache = HexStrikeCache(max_size=2, ttl=60)
        cache.set("cmd1", {}, {"ok": True})
        cache.get("cmd1", {})
        cache.get("missing", {})

        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert "hit_rate" in stats

    def test_advanced_cache_basic(self):
        from hexstrike.core.cache import AdvancedCache

        cache = AdvancedCache(max_size=2, default_ttl=60)
        cache.set("a", {"value": 1})
        assert cache.get("a")["value"] == 1
        assert cache.get("missing") is None

        stats = cache.get_stats()
        assert "hit_count" in stats
        assert "miss_count" in stats


class TestTelemetry:
    def test_record_execution(self, monkeypatch):
        from hexstrike.core.telemetry import TelemetryCollector

        telemetry = TelemetryCollector()
        monkeypatch.setattr(
            telemetry,
            "get_system_metrics",
            lambda: {
                "cpu_percent": 1.0,
                "memory_percent": 2.0,
                "disk_usage": 3.0,
                "network_io": {},
            },
        )

        telemetry.record_execution(True, 1.25)
        telemetry.record_execution(False, 0.75)

        stats = telemetry.get_stats()
        assert stats["commands_executed"] == 2
        assert stats["success_rate"] == "50.0%"
        assert "average_execution_time" in stats


class TestProcessManager:
    def test_register_status_list_cleanup(self):
        from hexstrike.core.process_manager import ProcessManager

        pid = 999999
        ProcessManager.cleanup_process(pid)

        ProcessManager.register_process(pid, "echo hexstrike-test", None)

        status = ProcessManager.get_process_status(pid)
        assert status is not None
        assert status["pid"] == pid
        assert status["command"] == "echo hexstrike-test"

        processes = ProcessManager.list_active_processes()
        assert pid in processes

        cleaned = ProcessManager.cleanup_process(pid)
        assert cleaned is not None
        assert ProcessManager.get_process_status(pid) is None

    def test_update_progress(self):
        from hexstrike.core.process_manager import ProcessManager

        pid = 999998
        ProcessManager.cleanup_process(pid)
        ProcessManager.register_process(pid, "sleep 1", None)

        ProcessManager.update_process_progress(
            pid,
            0.5,
            last_output="halfway",
            bytes_processed=123,
        )

        status = ProcessManager.get_process_status(pid)
        assert status["progress"] == 0.5
        assert status["last_output"] == "halfway"
        assert status["bytes_processed"] == 123
        assert "runtime" in status

        ProcessManager.cleanup_process(pid)


class TestVisualEngine:
    def test_banner(self):
        from hexstrike.core.visual_engine import ModernVisualEngine

        banner = ModernVisualEngine.create_banner()
        assert isinstance(banner, str)
        assert "HexStrike" in banner

    def test_progress_bar(self):
        from hexstrike.core.visual_engine import ModernVisualEngine

        bar = ModernVisualEngine.render_progress_bar(0.5, width=20, label="test")
        assert isinstance(bar, str)
        assert "50.0%" in bar

    def test_vulnerability_card(self):
        from hexstrike.core.visual_engine import ModernVisualEngine

        card = ModernVisualEngine.format_vulnerability_card(
            {
                "name": "Test Vulnerability",
                "severity": "high",
                "description": "Dummy finding",
            }
        )
        assert "Test Vulnerability" in card
        assert "HIGH" in card

    def test_tool_output(self):
        from hexstrike.core.visual_engine import ModernVisualEngine

        output = ModernVisualEngine.format_tool_output(
            "dummy",
            "found test\nerror example\nwarning example",
            success=True,
        )
        assert "DUMMY" in output
        assert "SUCCESS" in output


class TestExecutor:
    def test_enhanced_executor_echo(self):
        from hexstrike.core.executor import EnhancedCommandExecutor

        result = EnhancedCommandExecutor("echo hexstrike_executor_test", timeout=5).execute()

        assert result["success"] is True
        assert result["return_code"] == 0
        assert "hexstrike_executor_test" in result["stdout"]
        assert result["execution_time"] >= 0

    def test_execute_command_wrapper_if_cache_exists(self):
        """
        Test ini akan menangkap masalah umum:
        core/cache.py belum punya global instance `cache = HexStrikeCache()`.
        """
        from hexstrike.core.executor import execute_command

        result = execute_command("echo hexstrike_wrapper_test", use_cache=False)
        assert result["success"] is True
        assert "hexstrike_wrapper_test" in result["stdout"]
