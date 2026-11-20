"""Tests for message_check.py, render_message.py and interview_kit.py (self contained fixtures)."""
import csv
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hiring_fixtures import ROOT, TempDir, make_scorecard, run_main  # noqa: E402

import interview_kit as ik  # noqa: E402
import message_check as mc  # noqa: E402
import render_message as rm  # noqa: E402

GOOD_COLD = ("Subject: Bookkeeper role at Northlight\n\nHi Ada, I am hiring a bookkeeper at Northlight Home Services "
             "and your public portfolio shows monthly close work. The pay is 3,000 to 3,500 a month. "
             "Open to a 15 minute chat?\n\nReply STOP and I will not write again.\n")
EM, EN = "\u2014", "\u2013"


def levels(findings, level):
    return [f for f in findings if f[0] == level]


class MessageCheckTests(unittest.TestCase):
    def test_clean_cold_message_passes(self):
        self.assertEqual(mc.check_message(GOOD_COLD, "cold"), [])

    def test_unfilled_placeholders_in_both_styles(self):
        findings = mc.check_message("Hi {{candidate_first_name}}, I am [YOUR NAME]. Reply STOP to opt out.", "cold")
        text = " ".join(f[2] for f in findings)
        self.assertIn("{{candidate_first_name}}", text)
        self.assertIn("[YOUR NAME]", text)
        self.assertEqual(len(levels(findings, "ERROR")), 2)

    def test_template_mode_allows_variables(self):
        findings = mc.check_message("Hi {{candidate_first_name}}. Reply STOP to opt out.", "cold", template=True)
        self.assertEqual(findings, [])

    def test_markdown_links_are_not_placeholders(self):
        self.assertEqual(mc.check_message("See [our page](https://example.com) for details.", "candidate"), [])

    def test_cold_message_needs_stop_line(self):
        findings = mc.check_message("Hi Ada, would you like a chat about a role?", "cold")
        self.assertTrue(any("opt out" in f[2] for f in levels(findings, "ERROR")))
        self.assertEqual(mc.check_message("Hi Ada, thanks for applying.", "candidate"), [])

    def test_length_limits(self):
        long_note = "Channel: linkedin_connection\n\n" + "a" * 301 + "\nReply STOP to opt out."
        self.assertTrue(any("limit 300" in f[2] for f in mc.check_message(long_note, "cold")))
        sms = "Channel: sms\n\n" + "b" * 161
        self.assertTrue(any("limit 160" in f[2] for f in mc.check_message(sms, "candidate")))
        subject = "Subject: " + "c" * 61 + "\n\nHello there."
        self.assertTrue(any("Subject is 61" in f[2] for f in mc.check_message(subject, "candidate")))
        self.assertEqual(mc.check_message("Channel: sms\n\n" + "b" * 160, "candidate"), [])

    def test_spam_words_and_exclamations_warn(self):
        findings = mc.check_message("Act now, this is a limited time offer!! Reply STOP", "cold")
        warnings = " ".join(f[2] for f in levels(findings, "WARN"))
        self.assertIn("act now", warnings)
        self.assertIn("limited time", warnings)
        self.assertIn("exclamation", warnings)

    def test_invented_claim_risk_phrases_warn(self):
        findings = mc.check_message("I loved your recent post about hiring. Reply STOP", "cold")
        self.assertTrue(any("personal fact" in f[2] for f in levels(findings, "WARN")))

    def test_dashes_are_errors_with_line_numbers(self):
        findings = mc.check_message("Line one.\nLine two %s here. Reply STOP" % EM, "cold")
        errors = levels(findings, "ERROR")
        self.assertEqual(errors[0][1], 2)
        self.assertIn("Dash", errors[0][2])
        self.assertTrue(levels(mc.check_message("Range 3%s4. Reply STOP" % EN, "cold"), "ERROR"))
        self.assertTrue(levels(mc.check_message("A spaced - hyphen. Reply STOP", "cold"), "WARN"))

    def test_cli_exit_codes(self):
        with TempDir() as tmp:
            good, bad = tmp / "good.md", tmp / "bad.md"
            good.write_text(GOOD_COLD, encoding="utf-8")
            bad.write_text("Hi {{name}}", encoding="utf-8")
            self.assertEqual(run_main(mc, [str(good), "--kind", "cold"])[0], 0)
            code, out, _ = run_main(mc, [str(bad), "--kind", "cold"])
            self.assertEqual(code, 1)
            self.assertIn("ERROR line 1", out)
            self.assertEqual(run_main(mc, [str(tmp / "missing.md")])[0], 1)
            self.assertEqual(run_main(mc, [str(good), "--kind", "weird"])[0], 2)

    def test_real_message_templates_pass_in_template_mode_when_present(self):
        folder = ROOT / "templates" / "messages"
        files = sorted(folder.glob("*.md")) if folder.exists() else []
        if not files:
            self.skipTest("templates/messages not present yet")
        for path in files:
            findings = mc.check_message(path.read_text(encoding="utf-8"), "candidate", template=True)
            self.assertEqual(levels(findings, "ERROR"), [], "%s: %s" % (path.name, findings))


class RenderMessageTests(unittest.TestCase):
    def test_render_fills_variables_with_spaces_inside_braces(self):
        text, missing = rm.render("Hi {{ candidate_first_name }}, about {{role_title}}.", {"candidate_first_name": "Ada", "role_title": "Bookkeeper"})
        self.assertEqual(text, "Hi Ada, about Bookkeeper.")
        self.assertEqual(missing, [])

    def test_missing_and_empty_variables_fail(self):
        text, missing = rm.render("Hi {{a}} {{b}} {{a}}", {"a": "  ", "extra": "x"})
        self.assertEqual(missing, ["a", "b"])
        self.assertIn("{{a}}", text)

    def test_cli_writes_only_when_complete(self):
        with TempDir() as tmp:
            template, values, out = tmp / "t.md", tmp / "v.json", tmp / "d" / "out.md"
            template.write_text("Hi {{candidate_first_name}}. Reply STOP to opt out.", encoding="utf-8")
            values.write_text(json.dumps({"other": "x"}), encoding="utf-8")
            code, text, _ = run_main(rm, [str(template), "--vars", str(values), "--out", str(out)])
            self.assertEqual(code, 1)
            self.assertIn("candidate_first_name", text)
            self.assertFalse(out.exists())
            values.write_text(json.dumps({"candidate_first_name": "Ada"}), encoding="utf-8")
            code, _, _ = run_main(rm, [str(template), "--vars", str(values), "--out", str(out)])
            self.assertEqual(code, 0)
            self.assertEqual(out.read_text(encoding="utf-8"), "Hi Ada. Reply STOP to opt out.")

    def test_check_flag_blocks_a_cold_message_without_stop(self):
        with TempDir() as tmp:
            template, values, out = tmp / "t.md", tmp / "v.json", tmp / "out.md"
            template.write_text("Hi {{n}}, want a chat?", encoding="utf-8")
            values.write_text(json.dumps({"n": "Ada"}), encoding="utf-8")
            code, text, _ = run_main(rm, [str(template), "--vars", str(values), "--out", str(out), "--check", "cold"])
            self.assertEqual(code, 1)
            self.assertFalse(out.exists())

    def test_bad_inputs(self):
        with TempDir() as tmp:
            template, values = tmp / "t.md", tmp / "v.json"
            template.write_text("Hi {{n}}", encoding="utf-8")
            values.write_text("[1]", encoding="utf-8")
            self.assertEqual(run_main(rm, [str(template), "--vars", str(values)])[0], 1)
            values.write_text("{", encoding="utf-8")
            self.assertEqual(run_main(rm, [str(template), "--vars", str(values)])[0], 1)
            self.assertEqual(run_main(rm, [str(template), "--vars", str(tmp / "none.json")])[0], 1)


class InterviewKitTests(unittest.TestCase):
    def test_guide_has_every_criterion_questions_and_anchors(self):
        card = make_scorecard()
        guide = ik.build_guide(card)
        for criterion in card["criteria"]:
            self.assertIn(criterion["name"], guide)
        self.assertIn("Tell me about a campaign you ran", guide)
        self.assertIn("Good answer signs", guide)
        self.assertIn("4 did it and taught or improved it", guide)
        self.assertIn("Write a first email", guide)
        self.assertIn("Never ask", guide)
        self.assertIn("not legal advice", guide)
        self.assertNotIn(EM, guide)
        self.assertNotIn(EN, guide)

    def test_criteria_without_questions_get_a_generic_prompt(self):
        guide = ik.build_guide(make_scorecard())
        self.assertIn("Walk me through a real example from your own work that shows this", guide)

    def test_rating_sheet_rows_match_criteria(self):
        card = make_scorecard()
        rows = ik.sheet_rows(card, "C001", "Sam")
        self.assertEqual(len(rows), 5)
        self.assertEqual(sum(int(r["weight"]) for r in rows), 100)
        self.assertEqual(rows[0]["candidate_id"], "C001")
        self.assertEqual(rows[0]["level_0_to_4"], "")

    def test_cli_writes_both_files(self):
        with TempDir() as tmp:
            source = tmp / "card.json"
            source.write_text(json.dumps(make_scorecard()), encoding="utf-8")
            out = tmp / "kit"
            code, text, _ = run_main(ik, [str(source), "--out", str(out), "--candidate", "C007"])
            self.assertEqual(code, 0)
            self.assertTrue((out / "interview-guide.md").exists())
            with open(out / "rating-sheet.csv", newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 5)
            self.assertEqual(rows[0]["candidate_id"], "C007")
            self.assertEqual(list(rows[0].keys()), ik.SHEET_COLUMNS)

    def test_cli_errors(self):
        with TempDir() as tmp:
            self.assertEqual(run_main(ik, [str(tmp / "none.json")])[0], 1)
            bad = tmp / "bad.json"
            bad.write_text("[]", encoding="utf-8")
            self.assertEqual(run_main(ik, [str(bad), "--out", str(tmp / "o")])[0], 1)


if __name__ == "__main__":
    unittest.main()
