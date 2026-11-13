"""
Workflow module tests.
Run:
  uv run pytest tests/test_workflows.py -v
"""
import pytest

pytestmark = pytest.mark.unit


class TestBugBountyWorkflows:
    def test_reconnaissance_workflow(self):
        from hexstrike.workflows.bugbounty import BugBountyTarget, BugBountyWorkflowManager

        manager = BugBountyWorkflowManager()
        target = BugBountyTarget(domain="example.local")

        workflow = manager.create_reconnaissance_workflow(target)

        assert workflow["target"] == "example.local"
        assert workflow["tools_count"] > 0
        assert workflow["estimated_time"] > 0
        assert len(workflow["phases"]) > 0

    def test_vulnerability_hunting_workflow(self):
        from hexstrike.workflows.bugbounty import BugBountyTarget, BugBountyWorkflowManager

        manager = BugBountyWorkflowManager()
        target = BugBountyTarget(
            domain="example.local",
            priority_vulns=["rce", "sqli", "xss"],
        )

        workflow = manager.create_vulnerability_hunting_workflow(target)

        assert workflow["target"] == "example.local"
        assert workflow["priority_score"] > 0
        assert len(workflow["vulnerability_tests"]) == 3


class TestCTFManager:
    def test_ctf_challenge_to_dict(self):
        from hexstrike.workflows.ctf_manager import CTFChallenge

        challenge = CTFChallenge(
            name="Web1",
            category="web",
            description="Find SQL injection",
            points=100,
            difficulty="easy",
        )

        data = challenge.to_dict()
        assert data["name"] == "Web1"
        assert data["category"] == "web"
        assert data["points"] == 100

    def test_ctf_workflow(self):
        from hexstrike.workflows.ctf_manager import CTFChallenge, CTFWorkflowManager

        manager = CTFWorkflowManager()
        challenge = CTFChallenge(
            name="Web1",
            category="web",
            description="Find SQL injection in login form",
            points=100,
            difficulty="easy",
        )

        workflow = manager.create_ctf_challenge_workflow(challenge)

        assert workflow["challenge"] == "Web1"
        assert workflow["category"] == "web"
        assert workflow["estimated_time"] > 0
        assert 0 < workflow["success_probability"] <= 1
        assert len(workflow["workflow_steps"]) > 0


class TestCTFTools:
    def test_suggest_web_sqli_tools(self):
        from hexstrike.workflows.ctf_tools import CTFToolManager

        manager = CTFToolManager()
        tools = manager.suggest_tools_for_challenge(
            "SQL injection in login form with database backend",
            "web",
        )

        assert "sqlmap" in tools

    def test_suggest_forensics_image_tools(self):
        from hexstrike.workflows.ctf_tools import CTFToolManager

        manager = CTFToolManager()
        tools = manager.suggest_tools_for_challenge(
            "PNG image steganography challenge",
            "forensics",
        )

        assert any(tool in tools for tool in ["exiftool", "steghide", "zsteg"])

    def test_get_tool_command(self):
        from hexstrike.workflows.ctf_tools import CTFToolManager

        manager = CTFToolManager()
        command = manager.get_tool_command("strings", "/tmp/sample.bin")

        assert "strings" in command
        assert "/tmp/sample.bin" in command


class TestCTFAutomation:
    def test_auto_solve_returns_analysis_result(self):
        from hexstrike.workflows.ctf_manager import CTFChallenge
        from hexstrike.workflows.ctf_automation import CTFChallengeAutomator

        automator = CTFChallengeAutomator()
        challenge = CTFChallenge(
            name="Web1",
            category="web",
            description="Simple SQL injection challenge",
            difficulty="easy",
            points=100,
        )

        result = automator.auto_solve_challenge(challenge)

        assert result["challenge_id"] == "Web1"
        assert result["status"] in {"analysis_complete", "needs_manual_intervention", "solved"}
        assert "automated_steps" in result
        assert "confidence" in result


class TestCTFTeam:
    def test_team_strategy(self):
        from hexstrike.workflows.ctf_manager import CTFChallenge
        from hexstrike.workflows.ctf_team import CTFTeamCoordinator

        coordinator = CTFTeamCoordinator()

        challenges = [
            CTFChallenge(
                name="Web1",
                category="web",
                description="XSS",
                points=100,
                difficulty="easy",
            ),
            CTFChallenge(
                name="Crypto1",
                category="crypto",
                description="RSA weak key",
                points=200,
                difficulty="hard",
            ),
        ]

        team_skills = {
            "alice": ["web", "webapp"],
            "bob": ["crypto", "cryptography"],
        }

        strategy = coordinator.optimize_team_strategy(challenges, team_skills)

        assert "assignments" in strategy
        assert "priority_queue" in strategy
        assert "estimated_total_score" in strategy
        assert len(strategy["assignments"]) == 2
