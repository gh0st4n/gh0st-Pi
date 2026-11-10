"""
HexStrike AI - CTF Team Coordinator
"""
from typing import Dict, Any, List

from hexstrike.workflows.ctf_manager import CTFChallenge, ctf_manager
from hexstrike.core.logging import setup_logging

logger = setup_logging()


class CTFTeamCoordinator:
    """Coordinate team efforts in CTF competitions."""

    def __init__(self):
        self.team_members = {}
        self.challenge_assignments = {}

    def optimize_team_strategy(self, challenges: List[CTFChallenge],
                               team_skills: Dict[str, List[str]]) -> Dict[str, Any]:
        strategy = {
            "assignments": {},
            "priority_queue": [],
            "collaboration_opportunities": [],
            "estimated_total_score": 0,
        }

        skill_matrix = {}
        for member, skills in team_skills.items():
            skill_matrix[member] = {
                "web": any(s in ["web", "webapp"] for s in skills),
                "crypto": any(s in ["crypto", "cryptography"] for s in skills),
                "pwn": any(s in ["pwn", "binary"] for s in skills),
                "forensics": any(s in ["forensics", "investigation"] for s in skills),
                "rev": any(s in ["reverse", "reversing"] for s in skills),
                "osint": any(s in ["osint", "intelligence"] for s in skills),
                "misc": True,
            }

        member_scores = {}
        for member in team_skills:
            member_scores[member] = []
            for ch in challenges:
                base = ch.points
                mult = 1.5 if skill_matrix[member].get(ch.category, False) else 1.0
                diff_pen = {"easy": 1.0, "medium": 0.9, "hard": 0.7, "insane": 0.5, "unknown": 0.8}
                score = base * mult * diff_pen.get(ch.difficulty, 0.8)
                member_scores[member].append({"challenge": ch, "score": score})

        assignments = {m: [] for m in team_skills}
        assigned = set()
        for _ in range(len(challenges)):
            best = None; best_score = -1
            for member, scores in member_scores.items():
                for item in scores:
                    if item["challenge"].name not in assigned and item["score"] > best_score:
                        best_score = item["score"]
                        best = (member, item)
            if best:
                member, item = best
                assignments[member].append(item)
                assigned.add(item["challenge"].name)

        strategy["assignments"] = assignments
        all_items = []
        for member, items in assignments.items():
            for item in items:
                all_items.append({
                    "member": member,
                    "challenge": item["challenge"].name,
                    "priority": item["score"],
                })
        strategy["priority_queue"] = sorted(all_items, key=lambda x: x["priority"], reverse=True)
        strategy["estimated_total_score"] = sum(i["priority"] for i in all_items)

        for ch in challenges:
            if ch.difficulty in ["hard", "insane"]:
                relevant = [m for m, skills in team_skills.items()
                            if ch.category in [s.lower() for s in skills]]
                if len(relevant) >= 2:
                    strategy["collaboration_opportunities"].append({
                        "challenge": ch.name,
                        "recommended_team": relevant,
                    })

        return strategy


# Global instance
ctf_coordinator = CTFTeamCoordinator()