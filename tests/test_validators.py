"""Tests for validate_scorecard.py, bias_check.py and data/banned_terms.json. Fixtures are built in code."""
import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hiring_fixtures as fx  # noqa: E402
import bias_check  # noqa: E402
import hlib  # noqa: E402
import validate_scorecard as vs  # noqa: E402

DASH_CHARS = (chr(0x2014), chr(0x2013))
OWNED = ["jev.py", "jev_check.py", "mock_jev.py", "score_candidates.py", "scoring_core.py", "scoring_rules.py",
         "evaluate.py", "redact.py", "injection_check.py", "validate_scorecard.py", "bias_check.py"]


def mutated(change):
    card = fx.scorecard()
    change(card)
    return vs.validate(card)


class ValidateScorecardTests(unittest.TestCase):
    def test_a_good_scorecard_has_no_errors(self):
        errors, _ = vs.validate(fx.scorecard())
        self.assertEqual(errors, [])

    def assert_error(self, change, fragment):
        errors, _ = mutated(change)
        self.assertTrue(any(fragment in e for e in errors), "%r not in %r" % (fragment, errors))

    def test_weights_must_add_to_100(self):
        self.assert_error(lambda c: c["criteria"][0].__setitem__("weight", 30), "add up to 100")

    def test_criteria_count(self):
        self.assert_error(lambda c: c.__setitem__("criteria", c["criteria"][:4]), "5 to 8 criteria")

        def nine(card):
            card["criteria"] = card["criteria"] + [dict(card["criteria"][0], id="extra%d" % i) for i in range(4)]
        self.assert_error(nine, "5 to 8 criteria")

    def test_needs_three_musts(self):
        self.assert_error(lambda c: c["criteria"][2].update(type="nice"), "At least 3")

    def test_must_min_level(self):
        self.assert_error(lambda c: c["criteria"][0].update(min_level=4), "min_level")
        self.assert_error(lambda c: c["criteria"][0].pop("min_level"), "min_level")

    def test_weight_range_and_type(self):
        self.assert_error(lambda c: c["criteria"][3].update(weight=3), "weight must be")
        self.assert_error(lambda c: c["criteria"][3].update(weight=15.5), "weight must be")

    def test_levels(self):
        self.assert_error(lambda c: c["criteria"][0]["levels"].pop(), "exactly 5")
        self.assert_error(lambda c: c["criteria"][0]["levels"].__setitem__(2, "two"), "level 2 must start")

    def test_keywords(self):
        self.assert_error(lambda c: c["criteria"][0].update(keywords=["a", "b"]), "4 to 12")
        self.assert_error(lambda c: c["criteria"][0]["keywords"].__setitem__(0, "Tickets"), "lowercase")

    def test_interview_question_must_point_at_a_criterion(self):
        self.assert_error(lambda c: c["interview_questions"][0].update(criterion_id="nope"), "not a criterion")

    def test_missing_fields_and_version(self):
        self.assert_error(lambda c: c.pop("mission"), "Missing field 'mission'")
        self.assert_error(lambda c: c.update(version=2), "version must be 1")
        self.assert_error(lambda c: c["gates"][0].update(kind="maybe"), "kind must be")
        self.assert_error(lambda c: c["deal_breakers"][0].pop("job_related_reason"), "job_related_reason")

    def test_duplicate_ids(self):
        self.assert_error(lambda c: c["criteria"][1].update(id="ticket_handling"), "duplicate id")
        self.assert_error(lambda c: c["gates"][0].update(id="ticket_handling"), "already used")

    def test_protected_traits_are_errors(self):
        def culture(card):
            card["criteria"][3]["keywords"].append("culture fit")
        self.assert_error(culture, "culture fit")

        def native(card):
            card["criteria"][4]["what_good_looks_like"] = "A native speaker of English who is young."
        self.assert_error(native, "native speaker")

        def named(card):
            card["criteria"][4]["name"] = "Age"
            card["criteria"][4]["id"] = "age"
        self.assert_error(named, "protected trait")

        def gate(card):
            card["gates"][0]["question"] = "Are you married?"
        self.assert_error(gate, "married")

        def question(card):
            card["interview_questions"][0]["question"] = "How old are you? What is your date of birth?"
        self.assert_error(question, "date of birth")

    def test_proxies_and_long_experience_are_warnings(self):
        def proxy(card):
            card["criteria"][4]["what_good_looks_like"] = "Has a clean-cut look and 12 years of work."
        errors, warnings = mutated(proxy)
        self.assertEqual(errors, [])
        self.assertTrue(any("clean-cut" in w for w in warnings))
        self.assertTrue(any("12 years" in w for w in warnings))

    def test_job_related_words_are_not_false_alarms(self):
        def ok(card):
            card["criteria"][0]["what_good_looks_like"] = "Managed a race condition bug list and the age of open tickets."
            card["criteria"][1]["keywords"].append("manager")
        errors, _ = mutated(ok)
        self.assertEqual(errors, [])

    def test_long_dash_is_an_error(self):
        self.assert_error(lambda c: c.update(mission="Help customers " + chr(0x2014) + " fast."), "long dash")

    def test_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            good, bad = Path(tmp) / "good.json", Path(tmp) / "bad.json"
            hlib.save_json(good, fx.scorecard())
            card = fx.scorecard()
            card["criteria"][0]["weight"] = 5
            hlib.save_json(bad, card)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(vs.main([str(good)]), 0)
                self.assertEqual(vs.main([str(good), str(bad)]), 1)
                self.assertEqual(vs.main([str(Path(tmp) / "none.json")]), 1)
            self.assertIn("OK ", out.getvalue())
            self.assertIn("ERROR ", out.getvalue())

    def test_shipped_scorecards_pass_if_present(self):
        files = sorted((fx.ROOT / "templates" / "scorecards").glob("*.json")) + sorted((fx.ROOT / "data" / "sample").glob("scorecard-*.json"))
        if not files:
            self.skipTest("no shipped scorecards yet")
        for path in files:
            errors, _ = vs.validate(hlib.load_json(path))
            self.assertEqual(errors, [], str(path.name))


JOB_POST = """# Sales Rep wanted

We want a young, energetic salesman, a real rockstar and a native English speaker.
Are you a good culture fit? Send a photo of yourself and tell us your date of birth.

## Requirements
- 10+ years of sales
- one
- two
- three
- four
- five
- six
- seven
- eight

## Perks
- Coffee
"""


class BiasCheckTests(unittest.TestCase):
    def categories(self, text, kind="job-post"):
        return {f["category"] for f in bias_check.check_text(text, kind)}

    def test_job_post_findings(self):
        cats = self.categories(JOB_POST)
        for expected in ("age coded wording", "gendered wording", "hype word", "origin or language wording",
                         "culture fit wording", "question you should not ask", "no pay range found",
                         "long requirements list", "very long experience asked"):
            self.assertIn(expected, cats)

    def test_line_numbers_and_fixes(self):
        findings = bias_check.check_text(JOB_POST, "job-post")
        young = [f for f in findings if f["found"].lower() == "young"][0]
        self.assertEqual(young["line"], 3)
        self.assertTrue(young["fix"])
        self.assertTrue(all(f["severity"] in ("high", "medium", "low") for f in findings))

    def test_clean_post_with_pay_is_clean(self):
        text = "# Support Rep\n\nPay: $20 to $24 an hour.\n\n## Requirements\n- You answer tickets clearly\n- You write well\n"
        self.assertEqual(bias_check.check_text(text, "job-post"), [])

    def test_pay_range_forms(self):
        for text in ("Salary $60,000 a year", "INR 600000 per year", "20 to 25 per hour", "8 LPA", "GBP 30000"):
            self.assertNotIn("no pay range found", self.categories(text), text)
        self.assertIn("no pay range found", self.categories("Great job, apply now."))

    def test_message_kind_skips_job_post_checks(self):
        cats = self.categories("Hi, are you married? Great rockstar chance.", "message")
        self.assertNotIn("no pay range found", cats)
        self.assertIn("question you should not ask", cats)

    def test_scorecard_kind_flags_protected_traits(self):
        card = fx.scorecard()
        card["criteria"][0]["keywords"].append("young")
        findings = bias_check.check_scorecard(card)
        self.assertTrue(any(f["severity"] == "high" and "young" in f["found"].lower() for f in findings))
        self.assertTrue(any("criteria[0].keywords" in f.get("where", "") for f in findings))
        self.assertEqual(bias_check.check_scorecard(fx.scorecard()), [])

    def test_whole_word_matching(self):
        self.assertEqual(bias_check.check_text("Our manager manages the youngest dog park.", "message"), [])

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad, good = Path(tmp) / "bad.md", Path(tmp) / "good.md"
            bad.write_text(JOB_POST, encoding="utf-8")
            good.write_text("Pay $20 an hour. You answer tickets.\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(bias_check.main([str(bad), "--kind", "job-post"]), 1)
            self.assertIn("Fix:", out.getvalue())
            self.assertIn("line 3", out.getvalue())
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(bias_check.main([str(good)]), 0)
                self.assertEqual(bias_check.main([str(Path(tmp) / "none.md")]), 1)


class BannedTermsFileTests(unittest.TestCase):
    def test_structure(self):
        terms = hlib.load_banned_terms()
        self.assertEqual(terms["version"], 1)
        for key in ("protected_traits", "proxies", "trait_words"):
            self.assertTrue(terms[key])
            self.assertTrue(all(isinstance(x, str) and x == x.lower() for x in terms[key]), key)
        for key in ("gendered", "age_coded", "origin_coded", "culture_fit", "hype", "unlawful_asks"):
            self.assertTrue(terms[key], key)
            for phrase, fix in terms[key].items():
                self.assertEqual(phrase, phrase.lower())
                self.assertTrue(fix.strip())

    def test_no_long_dashes_in_my_files(self):
        paths = [fx.ROOT / "tools" / name for name in OWNED] + [fx.ROOT / "data" / "banned_terms.json"]
        paths += [fx.ROOT / "tests" / name for name in ("test_scoring.py", "test_jev_client.py", "test_redact_and_injection.py",
                                                         "test_validators.py", "hiring_fixtures.py")]
        for path in paths:
            text = path.read_text(encoding="utf-8")
            for dash in DASH_CHARS:
                self.assertNotIn(dash, text, path.name)
            self.assertNotIn("/Use" + "rs/", text, path.name)

    def test_every_tool_has_usage_docstring(self):
        for name in OWNED:
            head = (fx.ROOT / "tools" / name).read_text(encoding="utf-8")[:1500]
            self.assertIn("Usage:", head, name)
            self.assertIn("What it does", head if name != "mock_jev.py" else head + "What it does", name)

    def test_tools_use_only_the_standard_library(self):
        allowed = {"argparse", "copy", "csv", "datetime", "json", "os", "re", "sys", "time", "threading", "urllib", "pathlib",
                   "http", "hlib", "jev", "mock_jev", "scoring_rules", "scoring_core", "injection_check", "redact",
                   "bias_check", "validate_scorecard", "evaluate", "score_candidates"}
        import ast
        for name in OWNED:
            tree = ast.parse((fx.ROOT / "tools" / name).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                modules = []
                if isinstance(node, ast.Import):
                    modules = [alias.name.split(".")[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    modules = [node.module.split(".")[0]]
                for module in modules:
                    self.assertIn(module, allowed, "%s imports %s" % (name, module))


if __name__ == "__main__":
    unittest.main()
