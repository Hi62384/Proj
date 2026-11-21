"""Prompt contract regressions for the six-phase project workflow.

These tests guard the user-visible handoff contracts: research must not execute
or auto-advance, rechecks may succeed unchanged, and each execution goal has one
correct evidence-bearing next-phase command.
"""
from pathlib import Path
import re
import shlex
import unittest

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = (
    "PHASE_1_RESEARCH_MEGAPROMPT.md",
    "PHASE_1_IDEA_MEGAPROMPT.md",
    "PHASE_1_RECHECK_REPLACE_MEGAPROMPT.md",
    "PHASE_2_RELEASE_RESEARCH_MEGAPROMPT.md",
    "PHASE_2_RECHECK_MEGAPROMPT.md",
    "PHASE_3_MARKETING_RESEARCH_MEGAPROMPT.md",
    "PHASE_3_RECHECK_MEGAPROMPT.md",
)
RECHECKS = (RESEARCH[2], RESEARCH[4], RESEARCH[6])
EXECUTION = {
    4: ("PHASE_4_BUILD_MEGAPROMPT.md", "working_phase_5"),
    5: ("PHASE_5_RELEASE_MEGAPROMPT.md", "working_phase_6"),
    6: ("PHASE_6_MARKETING_MEGAPROMPT.md", "complete"),
}


def read(filename):
    return (ROOT / filename).read_text(encoding="utf-8")


class SixPhasePromptPolicyTests(unittest.TestCase):
    def test_research_outputs_full_pasteable_record_without_advancing(self):
        for filename in RESEARCH:
            with self.subTest(filename=filename):
                prompt = read(filename)
                self.assertFalse(prompt.startswith("/goal "))
                self.assertIn("single copyable code block", prompt)
                self.assertIn("full strict JSON frontmatter", prompt)
                self.assertIn("Do not create or require a downloadable file", prompt)
                self.assertIn("Pasting replaces the planning text but does not advance the phase", prompt)
                self.assertIn("project_update_base_sha256", prompt)
                self.assertIn("BASE_SHA256", prompt)
                self.assertIn("Preserve important previous research", prompt)
                self.assertIn("all important data and all important URLs", prompt)
                self.assertIn("2–21 calendar days total", prompt)
                self.assertIn("commercial_validation", prompt)
                self.assertNotIn("--phase complete", prompt)

    def test_rechecks_can_approve_without_forced_rewrite_or_replacement(self):
        for filename in RECHECKS:
            with self.subTest(filename=filename):
                prompt = read(filename)
                self.assertIn("Good to go — no substantive changes needed.", prompt)
                self.assertIn("Do not emit a replacement record or demand a paste", prompt)
                self.assertIn("Do not invent problems, force revisions, force replacement", prompt)
                self.assertIn("Optional cosmetic suggestions must not block", prompt)
                self.assertIn("not an endless internal loop", prompt)

    def test_phase_one_preserves_evidence_led_test_first_research(self):
        for filename in RESEARCH[:3]:
            with self.subTest(filename=filename):
                prompt = read(filename)
                for concept in ("TEST-FIRST GO", "Future TESTABLE hypothesis",
                                "fresh disconfirming research pass", "NO_GO",
                                "CONDITIONAL_PROOF_ONLY", "RESEARCH_BLOCKED",
                                "cheapest capable comparable paid alternative",
                                "acceptance criteria"):
                    self.assertIn(concept, prompt)
                self.assertIn("implementation-ready specification", prompt)
                self.assertIn("preserve `commercial_validation`", prompt)

    def test_release_research_connects_adjacent_targets_to_real_build_work(self):
        prompt = read("PHASE_2_RELEASE_RESEARCH_MEGAPROMPT.md")
        for concept in ("compatibility targets", "distribution destinations",
                        "adjacent ecosystems", "Unity pathfinding system",
                        "Revise the Phase 1 build specification", "Phase 4 build checklist",
                        "Phase 5 release checklist", "conditional", "deferred", "rejected"):
            self.assertIn(concept, prompt)
        self.assertIn("working_phase_2", prompt)
        self.assertIn("unreviewed", prompt)

    def test_marketing_research_covers_tactics_and_execution_dependencies(self):
        prompt = read("PHASE_3_MARKETING_RESEARCH_MEGAPROMPT.md")
        for concept in ("audiences", "positioning", "SEO", "conversion", "measurement",
                        "Phase 6 tasks", "Update Phase 1/4", "Update Phase 2/5",
                        "finite initial execution scope"):
            self.assertIn(concept, prompt)
        self.assertIn("working_phase_3", prompt)

    def test_each_goal_has_only_its_own_sequential_evidence_handoff(self):
        for phase, (filename, next_phase) in EXECUTION.items():
            with self.subTest(phase=phase):
                prompt = read(filename)
                self.assertTrue(prompt.startswith("/goal "))
                self.assertIn(f"Required phase: `working_phase_{phase}`", prompt)
                commands = re.findall(r"(?m)^\s*python -m portfolio_manager\.project_lifecycle set-phase .+$", prompt)
                self.assertEqual(len(commands), 1)
                argv = shlex.split(commands[0])
                self.assertEqual(argv[argv.index("--phase") + 1], next_phase)
                self.assertEqual(argv[argv.index("--actor") + 1], "codex")
                self.assertTrue(argv[argv.index("--evidence") + 1].strip())
                self.assertIn("Stop after that handoff", prompt)
                self.assertIn("Do not silently execute the next phase", prompt)
                if phase == 6:
                    self.assertIn("--description", argv)
                    self.assertIn("--sale-url", argv)
                    self.assertIn("--marketing-url", argv)
                else:
                    self.assertNotIn("--phase complete", prompt)

    def test_execution_requires_progress_important_data_and_shared_time_budget(self):
        for phase, (filename, _) in EXECUTION.items():
            with self.subTest(phase=phase):
                prompt = read(filename)
                self.assertIn(f"Phase {phase} completion estimate: N% (best guess)", prompt)
                self.assertIn("At **every checkpoint** update project.md and report in chat", prompt)
                self.assertIn("Any important data or URLs", prompt)
                for concept in ("edit/admin", "sale/download", "submission", "versions/hashes",
                                "remaining `[ ]` tasks", "2–21 calendar days total",
                                "not another three weeks for each phase", "Empty project"):
                    self.assertIn(concept, prompt)
                self.assertIn("preserve the current phase", prompt)
                self.assertIn("Never save passwords", prompt)

    def test_old_filename_redirects_cannot_execute_obsolete_goals(self):
        redirects = (
            "BUSINESS_OPPORTUNITY_RESEARCH_MEGAPROMPT.md",
            "BUSINESS_IDEA_TO_PROJECT_MEGAPROMPT.md",
            "PHASE_2_DEVELOPMENT_MEGAPROMPT.md",
            "PHASE_3A_RESEARCH_MEGAPROMPT.md",
            "PHASE_3B_VALIDATION_MEGAPROMPT.md",
            "PHASE_3_MARKETING_MEGAPROMPT.md",
            "PHASE_4_EXECUTION_MEGAPROMPT.md",
        )
        for filename in redirects:
            with self.subTest(filename=filename):
                prompt = read(filename)
                self.assertIn("Retired prompt filename", prompt)
                self.assertNotIn("python -m portfolio_manager.project_lifecycle", prompt)
                self.assertFalse(prompt.startswith("/goal "))
                links = re.findall(r"\]\((PHASE_[A-Z0-9_]+\.md)\)", prompt)
                self.assertTrue(links)
                self.assertTrue(all((ROOT / link).is_file() for link in links))


if __name__ == "__main__":
    unittest.main()
