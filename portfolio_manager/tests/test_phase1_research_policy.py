"""Regression tests for evidence-led, test-first Phase 1 research prompt policy."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
PROMPTS = (
    "BUSINESS_OPPORTUNITY_RESEARCH_MEGAPROMPT.md",
    "BUSINESS_IDEA_TO_PROJECT_MEGAPROMPT.md",
    "PHASE_1_RECHECK_REPLACE_MEGAPROMPT.md",
)


class TestFirstResearchPolicyTests(unittest.TestCase):
    def test_all_prompts_allow_test_first_go_without_fabricated_sales(self):
        for filename in PROMPTS:
            with self.subTest(filename=filename):
                prompt = (ROOT / filename).read_text(encoding="utf-8")
                self.assertIn("TEST-FIRST GO", prompt)
                self.assertIn("Future TESTABLE hypothesis", prompt)
                self.assertIn("GO_TO_PHASE_B", prompt)
                self.assertIn("CONDITIONAL_PROOF_ONLY", prompt)
                self.assertIn("RESEARCH_BLOCKED", prompt)
                self.assertIn("NO_GO", prompt)
                self.assertIn("commercial_validation", prompt)

    def test_original_phase_one_prompts_still_red_team(self):
        for filename in PROMPTS[:2]:
            with self.subTest(filename=filename):
                prompt = (ROOT / filename).read_text(encoding="utf-8")
                self.assertIn("fresh disconfirming research pass", prompt)
                self.assertIn("TEST-FIRST / commercially unvalidated", prompt)
                self.assertIn("cheapest", prompt)

    def test_copy_footer_does_not_force_verified_customer_sales(self):
        ui = (ROOT / "portfolio_manager/workspace_window.py").read_text(encoding="utf-8")
        self.assertIn("TEST-FIRST GO", ui)
        self.assertIn("post-launch TESTABLE assumptions", ui)
        self.assertNotIn("GO_TO_PHASE_B requires source-backed PASS on every applicable hard gate", ui)

    def test_phase_two_starts_with_bound_proof_and_keeps_release_gate(self):
        phase2 = (ROOT / "PHASE_2_DEVELOPMENT_MEGAPROMPT.md").read_text(encoding="utf-8")
        self.assertIn("TEST-FIRST", phase2)
        self.assertIn("stop/pivot criteria", phase2)
        self.assertIn("Do not demand paid buyers", phase2)
        self.assertIn("working_phase_3", phase2)


if __name__ == "__main__":
    unittest.main()
