"""Test semua module bisa diimport dengan benar."""
import pytest


CORE_MODULES = [
    "hexstrike",
    "hexstrike.config",
    "hexstrike.core",
    "hexstrike.core.colors",
    "hexstrike.core.cache",
    "hexstrike.core.telemetry",
    "hexstrike.core.executor",
    "hexstrike.core.process_manager",
    "hexstrike.core.visual_engine",
    "hexstrike.core.logging",
]

INTELLIGENCE_MODULES = [
    "hexstrike.intelligence",
    "hexstrike.intelligence.models",
    "hexstrike.intelligence.decision_engine",
    "hexstrike.intelligence.parameter_optimizer",
    "hexstrike.intelligence.technology_detector",
    "hexstrike.intelligence.rate_limiter",
]

ERROR_HANDLING_MODULES = [
    "hexstrike.error_handling",
    "hexstrike.error_handling.models",
    "hexstrike.error_handling.handler",
    "hexstrike.error_handling.recovery",
    "hexstrike.error_handling.degradation",
]

WORKFLOW_MODULES = [
    "hexstrike.workflows",
    "hexstrike.workflows.bugbounty",
    "hexstrike.workflows.ctf_manager",
    "hexstrike.workflows.ctf_tools",
    "hexstrike.workflows.ctf_automation",
    "hexstrike.workflows.ctf_team",
]

VULN_INTEL_MODULES = [
    "hexstrike.vuln_intel",
    "hexstrike.vuln_intel.cve_manager",
    "hexstrike.vuln_intel.exploit_generator",
    "hexstrike.vuln_intel.correlator",
]

WEB_TESTING_MODULES = [
    "hexstrike.web_testing",
    "hexstrike.web_testing.http_framework",
    "hexstrike.web_testing.payload_generator",
]

INFRASTRUCTURE_MODULES = [
    "hexstrike.infrastructure",
    "hexstrike.infrastructure.process_pool",
    "hexstrike.infrastructure.resource_monitor",
    "hexstrike.infrastructure.performance",
    "hexstrike.infrastructure.env_manager",
]

UTILS_MODULES = [
    "hexstrike.utils",
    "hexstrike.utils.file_ops",
]


ALL_MODULES = (
    CORE_MODULES + INTELLIGENCE_MODULES + ERROR_HANDLING_MODULES +
    WORKFLOW_MODULES + VULN_INTEL_MODULES + WEB_TESTING_MODULES +
    INFRASTRUCTURE_MODULES + UTILS_MODULES
)


@pytest.mark.unit
class TestImports:
    """Test semua module bisa diimport."""

    @pytest.mark.parametrize("module_name", ALL_MODULES)
    def test_import_module(self, module_name):
        """Test import setiap module."""
        __import__(module_name)

    def test_import_hexstrike_package(self):
        """Test import package utama."""
        import hexstrike
        assert hexstrike.__version__ == "6.0.0"

    def test_config_values(self):
        """Test konfigurasi default."""
        from hexstrike.config import API_PORT, API_HOST, COMMAND_TIMEOUT
        assert API_PORT == 8888
        assert API_HOST == "127.0.0.1"
        assert COMMAND_TIMEOUT == 300


@pytest.mark.unit
class TestCoreModules:
    """Test core modules functionality."""

    def test_colors_exist(self):
        from hexstrike.core.colors import HexStrikeColors
        assert hasattr(HexStrikeColors, "RED")
        assert hasattr(HexStrikeColors, "SUCCESS")
        assert hasattr(HexStrikeColors, "HACKER_RED")
        assert hasattr(HexStrikeColors, "PRIMARY_BORDER")

    def test_cache_operations(self):
        from hexstrike.core.cache import HexStrikeCache
        cache = HexStrikeCache(max_size=10, ttl=60)
        cache.set("cmd1", {"p": 1}, {"result": "ok"})
        result = cache.get("cmd1", {"p": 1})
        assert result is not None
        assert result["result"] == "ok"

    def test_telemetry(self):
        from hexstrike.core.telemetry import TelemetryCollector
        t = TelemetryCollector()
        t.record_execution(True, 1.5)
        t.record_execution(False, 0.5)
        stats = t.get_stats()
        assert stats["commands_executed"] == 2

    def test_visual_engine_banner(self):
        from hexstrike.core.visual_engine import ModernVisualEngine
        banner = ModernVisualEngine.create_banner()
        assert "HexStrike" in banner

    def test_process_manager(self):
        from hexstrike.core.process_manager import ProcessManager
        ProcessManager.register_process(99999, "test", None)
        status = ProcessManager.get_process_status(99999)
        assert status is not None
        ProcessManager.cleanup_process(99999)


@pytest.mark.unit
class TestIntelligenceModules:
    """Test intelligence modules."""

    def test_target_profile(self):
        from hexstrike.intelligence.models import TargetProfile, TargetType
        profile = TargetProfile(target="example.com")
        assert profile.target == "example.com"
        assert profile.target_type == TargetType.UNKNOWN

    def test_decision_engine_web(self):
        from hexstrike.intelligence.decision_engine import decision_engine
        from hexstrike.intelligence.models import TargetType
        profile = decision_engine.analyze_target("http://example.com")
        assert profile.target_type == TargetType.WEB_APPLICATION

    def test_decision_engine_ip(self):
        from hexstrike.intelligence.decision_engine import decision_engine
        from hexstrike.intelligence.models import TargetType
        profile = decision_engine.analyze_target("192.168.1.1")
        assert profile.target_type == TargetType.NETWORK_HOST

    def test_select_tools(self):
        from hexstrike.intelligence.decision_engine import decision_engine
        profile = decision_engine.analyze_target("http://example.com")
        tools = decision_engine.select_optimal_tools(profile, "quick")
        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_attack_chain(self):
        from hexstrike.intelligence.decision_engine import decision_engine
        profile = decision_engine.analyze_target("http://example.com")
        chain = decision_engine.create_attack_chain(profile)
        assert len(chain.steps) > 0
        assert 0 < chain.success_probability <= 1

    def test_rate_limiter(self):
        from hexstrike.intelligence.rate_limiter import RateLimitDetector
        detector = RateLimitDetector()
        result = detector.detect_rate_limiting("Too Many Requests", 429)
        assert result["detected"] is True


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling modules."""

    def test_error_classification(self):
        from hexstrike.error_handling.handler import IntelligentErrorHandler
        from hexstrike.error_handling.models import ErrorType
        handler = IntelligentErrorHandler()
        assert handler.classify_error("Connection timed out") == ErrorType.TIMEOUT
        assert handler.classify_error("Permission denied") == ErrorType.PERMISSION_DENIED

    def test_recovery_strategy(self):
        from hexstrike.error_handling.handler import IntelligentErrorHandler
        handler = IntelligentErrorHandler()
        strategy = handler.handle_tool_failure(
            "nmap", TimeoutError("timeout"), {"target": "test"}
        )
        assert strategy is not None
        assert strategy.action is not None

    def test_degradation_fallback(self):
        from hexstrike.error_handling.degradation import GracefulDegradation
        manager = GracefulDegradation()
        chain = manager.create_fallback_chain("network_discovery", ["nmap"])
        assert isinstance(chain, list)
        assert "nmap" not in chain


@pytest.mark.unit
class TestWorkflows:
    """Test workflow modules."""

    def test_bugbounty_recon(self):
        from hexstrike.workflows.bugbounty import BugBountyTarget, BugBountyWorkflowManager
        manager = BugBountyWorkflowManager()
        target = BugBountyTarget(domain="example.com")
        workflow = manager.create_reconnaissance_workflow(target)
        assert workflow["target"] == "example.com"
        assert len(workflow["phases"]) > 0

    def test_ctf_workflow(self):
        from hexstrike.workflows.ctf_manager import CTFChallenge, CTFWorkflowManager
        manager = CTFWorkflowManager()
        challenge = CTFChallenge(
            name="Test", category="web", description="SQLi",
            points=100, difficulty="easy"
        )
        workflow = manager.create_ctf_challenge_workflow(challenge)
        assert workflow["challenge"] == "Test"
        assert workflow["estimated_time"] > 0

    def test_ctf_tool_suggestions(self):
        from hexstrike.workflows.ctf_tools import CTFToolManager
        manager = CTFToolManager()
        tools = manager.suggest_tools_for_challenge("SQL injection", "web")
        assert "sqlmap" in tools