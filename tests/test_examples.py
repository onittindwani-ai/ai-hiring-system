"""Runs the offline examples as separate programs and checks they finish and print their key lines.

Usage:
    python3 -m unittest tests.test_examples
"""
import subprocess
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"


def run_example(name):
    started = time.time()
    result = subprocess.run([sys.executable, str(EXAMPLES / name)], capture_output=True, text=True, cwd=str(ROOT), timeout=60)
    return result, time.time() - started


class ExampleTests(unittest.TestCase):
    def test_full_demo_runs_offline_and_fast(self):
        result, seconds = run_example("01_full_demo.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for line in ("1. New role folder", "2. Plan the money", "5. Score the 20 made up candidates blind",
                     "engine: rules", "engine: mock", "FAKE Jev for practice", "6. Shortlist", "7. Two message drafts",
                     "Nothing is sent", "SUMMARY"):
            self.assertIn(line, result.stdout)
        self.assertLess(seconds, 20)

    def test_mock_jev_screening_runs_and_says_it_is_fake(self):
        result, seconds = run_example("03_screen_with_mock_jev.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("FAKE Jev for practice", result.stdout)
        self.assertIn("THE WHOLE FLOW for 20 bookkeeper candidates", result.stdout)
        self.assertIn("Agreement with the hand written answer key", result.stdout)
        self.assertLess(seconds, 20)

    def test_sourcing_week_marks_a_stopped_person(self):
        result, _ = run_example("02_sourcing_week.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("is now stopped", result.stdout)
        contactable = result.stdout.split("Who may still be contacted")[1]
        self.assertNotIn("Tomas Example", contactable)
        self.assertIn("Ana Example", contactable)

    def test_batch_math_plans_extra_offers(self):
        result, _ = run_example("04_batch_hiring_math.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Make 7 offers to land 5 hires", result.stdout)
        self.assertIn("backup list", result.stdout)

    def test_weekly_review_lists_stuck_people(self):
        result, _ = run_example("05_weekly_review.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Stuck for more than 7 days", result.stdout)
        self.assertIn("Nothing is sent, posted or rejected without the owner's yes.", result.stdout)

    def test_every_example_has_usage_in_its_docstring(self):
        files = sorted(EXAMPLES.glob("0*.py"))
        self.assertEqual(len(files), 5)
        for path in files:
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith('"""'), path.name)
            self.assertIn("Usage:", text, path.name)


if __name__ == "__main__":
    unittest.main()
