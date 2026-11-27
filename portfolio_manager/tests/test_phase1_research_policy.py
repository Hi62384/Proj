"""Four-phase prompt contracts, stage gates, final import and execution goals."""
from pathlib import Path
import re
import shlex
import unittest

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = (
    "PHASE_1_RESEARCH_MEGAPROMPT.md",
    "PHASE_1_IDEA_MEGAPROMPT.md",
    "PHASE_1_RECHECK_REPLACE_MEGAPROMPT.md",
)
RECHECKS = (RESEARCH[2],)
EXECUTION = {
    2: ("PHASE_2_BUILD_MEGAPROMPT.md", "working_phase_3"),
    3: ("PHASE_3_RELEASE_MEGAPROMPT.md", "working_phase_4"),
    4: ("PHASE_4_MARKETING_MEGAPROMPT.md", "complete"),
}


def read(filename):
    return (ROOT / filename).read_text(encoding="utf-8")


class FourPhasePromptPolicyTests(unittest.TestCase):
    def test_research_outputs_full_record_preserving_stored_phase(self):
        for filename in RESEARCH:
            with self.subTest(filename=filename):
                prompt = read(filename)
                self.assertFalse(prompt.startswith("/goal "))
                self.assertIn("single copyable code block", prompt)
                self.assertIn("full strict JSON frontmatter", prompt)
                self.assertIn("Do not create or require a downloadable file", prompt)
                self.assertIn("stored project_phase", prompt)
                self.assertIn("project_update_phase_1b", prompt)
                self.assertIn("project_update_base_sha256", prompt)
                self.assertIn("BASE_SHA256", prompt)
                self.assertIn("Preserve important previous research", prompt)
                self.assertIn("all important data and all important URLs", prompt)
                self.assertIn("2–21 calendar days total", prompt)
                self.assertIn("commercial_validation", prompt)
                self.assertNotIn("--phase complete", prompt)

    def test_phase_one_a_checks_each_stage_before_proceeding(self):
        for filename in RESEARCH[:2]:
            with self.subTest(filename=filename):
                prompt = read(filename)
                first = prompt.index("# Stage 1 — Product research and internal verification")
                second = prompt.index("# Stage 2 — Release research and internal verification")
                third = prompt.index("# Stage 3 — Marketing research and internal verification")
                self.assertLess(first, prompt.index("Stage 1 exit gate"))
                self.assertLess(prompt.index("Stage 1 exit gate"), second)
                self.assertLess(second, prompt.index("Stage 2 exit gate"))
                self.assertLess(prompt.index("Stage 2 exit gate"), third)
                self.assertLess(third, prompt.index("Stage 3 exit gate"))
                self.assertIn("Do not set project_update_phase_1b", prompt)
                self.assertIn('No intermediate pastes', prompt)
                self.assertIn('on "continue"', prompt)

    def test_recheck_approves_without_forced_rewrite_but_returns_full_final_record(self):
        prompt = read(RESEARCH[2])
        self.assertIn("Good to go — no substantive changes needed.", prompt)
        self.assertIn("Do not invent problems, force revisions, force replacement", prompt)
        self.assertIn("Optional cosmetic suggestions must not block", prompt)
        self.assertIn("not an endless internal loop", prompt)
        self.assertIn("ALWAYS return the entire final record", prompt)
        self.assertIn('"project_update_phase_1b": "verified"', prompt)
        self.assertIn("all three are approved", prompt)
        self.assertIn("automatically advances to Phase 2", prompt)
        self.assertIn("# Stage 2 — Independent release verification", prompt)
        self.assertIn("# Stage 3 — Independent marketing verification", prompt)
        self.assertIn("# Final cross-stage gate", prompt)

    def test_phase_one_recheck_requires_source_backed_independent_depth(self):
        prompt = read("PHASE_1_RECHECK_REPLACE_MEGAPROMPT.md")
        for requirement in ("Minimum evidence standard — depth before approval",
                            "Buyer-side evidence", "Competition from the buyer's perspective",
                            "Commercial practicality", "Fresh disconfirmation",
                            "Implementation-specification audit",
                            "8–15 distinct, relevant direct-source pages",
                            "coverage guide, not a mechanical quota",
                            "three strongest material objections",
                            "NEW", "RECHECKED", "UNVERIFIED",
                            "not an independently verified GO",
                            "do not prolong work to meet a time target"):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, prompt)
        self.assertIn("Good to go — no substantive changes needed.", prompt)
        self.assertIn("Always return the full final project record", prompt)

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

    def test_initial_phase_one_research_finalists_get_deep_skeptical_evidence(self):
        for filename in ("PHASE_1_RESEARCH_MEGAPROMPT.md", "PHASE_1_IDEA_MEGAPROMPT.md"):
            with self.subTest(filename=filename):
                prompt = read(filename)
                for requirement in (
                    "Mandatory finalist verification — research depth before project creation",
                    "BEFORE final GO", "Independent buyer evidence",
                    "End-to-end competitive evidence", "Price, feasibility and access",
                    "Separate adversarial search", "Build-readiness audit",
                    "8–15 relevant, distinct source pages", "coverage guide, not a mandatory count or time quota",
                    "three strongest counterfindings", "PASS / FAIL / UNKNOWN",
                    "next-best finalist", "5, 30 or 60 minutes", "TEST-FIRST",
                    "exact direct source URL", "observation/access date",
                ):
                    self.assertIn(requirement, prompt)
                self.assertLess(prompt.index("Mandatory finalist verification"),
                                prompt.index("## Detailed Phase 1 specification"))

    def test_initial_phase_one_does_not_end_after_first_failed_finalist(self):
        for filename in ("PHASE_1_RESEARCH_MEGAPROMPT.md", "PHASE_1_IDEA_MEGAPROMPT.md"):
            with self.subTest(filename=filename):
                prompt = read(filename)
                for requirement in (
                    "Candidate rejection and niche-wide NO_GO exit gate",
                    "IDEA_NO_GO", "within the same invocation",
                    "finalist B", "distinct C", "at least three substantively different",
                    "not a numeric pass/fail quota", "What new direction was explored",
                    "RESEARCH_BLOCKED", "CONDITIONAL_PROOF_ONLY",
                    "If research/tool/context limits prevent",
                    "not a claim that every imaginable business was exhausted",
                    "no endless background loop",
                ):
                    self.assertIn(requirement, prompt)
                self.assertLess(prompt.index("Candidate rejection and niche-wide NO_GO exit gate"),
                                prompt.index("## Detailed Phase 1 specification"))
        owner_idea = read("PHASE_1_IDEA_MEGAPROMPT.md")
        self.assertIn("Additional rule for owner-supplied ideas", owner_idea)
        self.assertIn("no in-scope variation is viable", owner_idea)
        self.assertIn("not as a stealth rewrite", owner_idea)

    def test_release_and_marketing_requirements_survive_combining(self):
        for filename in RESEARCH[:2]:
            prompt = read(filename)
            for concept in ("compatibility targets", "distribution destinations",
                            "adjacent ecosystems", "Unity pathfinding system",
                            "Phase 2 build checklist", "Phase 3 release checklist",
                            "conditional", "deferred", "rejected", "audiences",
                            "positioning", "SEO", "conversion", "measurement",
                            "Phase 4 tasks", "finite initial execution scope"):
                self.assertIn(concept, prompt)
        recheck = read(RESEARCH[2])
        self.assertIn("direct/adjacent discovery matrix", recheck)
        self.assertIn("finite tasks", recheck)

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
                self.assertEqual(argv[argv.index("--workflow-version") + 1], "3")
                if phase == 4:
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
            "PHASE_2_RELEASE_RESEARCH_MEGAPROMPT.md",
            "PHASE_2_RECHECK_MEGAPROMPT.md",
            "PHASE_3_MARKETING_RESEARCH_MEGAPROMPT.md",
            "PHASE_3_RECHECK_MEGAPROMPT.md",
            "PHASE_4_BUILD_MEGAPROMPT.md",
            "PHASE_5_RELEASE_MEGAPROMPT.md",
            "PHASE_6_MARKETING_MEGAPROMPT.md",
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
