"""Tests for make_search_strings.py, prospects.py and make_form_script.py (self contained fixtures)."""
import json
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hiring_fixtures import ROOT, TempDir, make_scorecard, run_main  # noqa: E402

import make_form_script as mfs  # noqa: E402
import make_search_strings as mss  # noqa: E402
import prospects as pr  # noqa: E402
from hlib import PROSPECT_COLUMNS, read_csv, write_csv  # noqa: E402

DASHES = ("\u2012", "\u2013", "\u2014", "\u2015")


class SearchStringTests(unittest.TestCase):
    def setUp(self):
        self.card = make_scorecard()

    def test_every_platform_block_says_who_runs_it(self):
        strings = mss.build_strings(self.card, "Austin")
        for name in ("google_xray_linkedin", "linkedin_search", "indeed_search", "naukri_search", "wellfound"):
            self.assertIn(name, strings)
            self.assertTrue(strings[name]["runner"])
        self.assertIn("Claude", strings["google_xray_linkedin"]["runner"])
        self.assertIn("YOU", strings["linkedin_search"]["runner"])
        self.assertIn("YOU", strings["indeed_search"]["runner"])

    def test_strings_use_title_synonyms_and_must_keywords(self):
        text = mss.build_strings(self.card)["linkedin_search"]["string"]
        self.assertIn('"Sales Development Rep"', text)
        self.assertIn("sdr", text.lower())
        self.assertIn('"cold calling"', text)
        self.assertIn("NOT (intern OR recruiter OR student)", text)

    def test_location_and_remote_handling(self):
        multi = mss.build_strings(self.card, "Austin|Remote")["google_xray_linkedin"]["string"]
        self.assertIn("Austin", multi)
        self.assertIn("remote", multi)
        self.assertEqual(mss.location_clause(mss.locations("")), "")
        self.assertEqual(mss.location_clause(["New York"]), '"New York"')

    def test_quote_is_safe(self):
        self.assertEqual(mss.quote('say "hello" there'), '"say hello there"')
        self.assertEqual(mss.quote("crm"), "crm")
        self.assertNotIn('""', mss.quote('"'))

    def test_or_group_respects_length_hint(self):
        terms = ["term number %d" % i for i in range(40)]
        group = mss.or_group(terms, 100)
        self.assertLess(len(group), 110)
        self.assertGreater(group.count(" OR "), 1)

    def test_seniority_words_extend_titles(self):
        text = mss.build_strings(self.card, "", ["senior"])["linkedin_search"]["string"]
        self.assertIn('"senior Sales Development Rep"', text)

    def test_page_has_what_not_to_do_and_no_dashes_or_emails(self):
        strings = mss.build_strings(self.card, "Austin")
        page = mss.render(self.card, strings, "Austin")
        self.assertIn("What not to do", page)
        self.assertIn("Never scrape", page)
        self.assertIn("guess or buy private email", page)
        self.assertNotIn("@", page)
        for dash in DASHES:
            self.assertNotIn(dash, page)

    def test_github_only_for_technical_roles(self):
        self.assertNotIn("github", mss.build_strings(self.card))
        tech = make_scorecard()
        tech["title"] = "Backend Engineer"
        self.assertIn("github", mss.build_strings(tech, "Berlin"))
        self.assertIn('location:Berlin', mss.build_strings(tech, "Berlin")["github"]["string"])

    def test_cli_writes_file_and_fails_on_missing_input(self):
        with TempDir() as tmp:
            card = tmp / "card.json"
            card.write_text(json.dumps(self.card), encoding="utf-8")
            out = tmp / "out" / "strings.md"
            code, text, _ = run_main(mss, [str(card), "--location", "Austin", "--out", str(out)])
            self.assertEqual(code, 0)
            self.assertTrue(out.exists())
            bad = tmp / "bad.json"
            bad.write_text("[]", encoding="utf-8")
            self.assertEqual(run_main(mss, [str(bad)])[0], 1)
            self.assertEqual(run_main(mss, [str(tmp / "nope.json")])[0], 1)

    def test_runs_on_real_templates_when_present(self):
        folder = ROOT / "templates" / "scorecards"
        files = sorted(folder.glob("*.json")) if folder.exists() else []
        if not files:
            self.skipTest("templates/scorecards not present yet")
        for path in files:
            code, out, _ = run_main(mss, [str(path)])
            self.assertEqual(code, 0, path.name)


class ProspectTests(unittest.TestCase):
    def setUp(self):
        self._tmp = TempDir()
        self.tmp = self._tmp.__enter__()
        self.args = ["--role", "r1", "--base", str(self.tmp)]
        run_main(pr, ["init", "r1", "--base", str(self.tmp)])
        self.path = self.tmp / "r1" / "prospects.csv"

    def tearDown(self):
        self._tmp.__exit__()

    def add(self, name, url, extra=()):
        return run_main(pr, ["add"] + self.args + ["--name", name, "--url", url, "--location", "Austin"] + list(extra))

    def test_add_and_dedupe_by_url_and_by_name_location(self):
        self.assertEqual(self.add("Ada Example", "https://example.com/in/ada")[0], 0)
        _, out, _ = self.add("Someone Else", "http://www.example.com/in/ada/?utm=1")
        self.assertIn("Already on the list", out)
        _, out, _ = self.add("ada example", "https://example.org/other")
        self.assertIn("Already on the list", out)
        self.assertEqual(len(read_csv(self.path)), 1)
        self.assertEqual(read_csv(self.path)[0]["prospect_id"], "P001")

    def test_dedupe_command_removes_existing_duplicates(self):
        row = {"prospect_id": "P001", "role_id": "r1", "name": "A", "public_url": "https://example.com/a", "location": "X",
               "source": "google_search", "contact_status": "not_contacted", "opt_out": "no"}
        write_csv(self.path, PROSPECT_COLUMNS, [row, dict(row, prospect_id="P002", public_url="https://example.com/a/")])
        code, out, _ = run_main(pr, ["dedupe"] + self.args)
        self.assertEqual(code, 0)
        self.assertIn("Removed 1", out)
        self.assertEqual(len(read_csv(self.path)), 1)

    def test_private_email_refused_unless_allowed(self):
        code, out, _ = self.add("Bo", "https://example.com/bo", ["--notes", "bo.private@example.com"])
        self.assertEqual(code, 1)
        self.assertIn("email", out)
        self.assertEqual(self.add("Bo", "https://example.com/bo", ["--notes", "bo.work@example.com", "--allow-email"])[0], 0)

    def test_bad_url_and_unknown_source_refused(self):
        self.assertEqual(self.add("Cy", "not a url")[0], 1)
        self.assertEqual(self.add("Cy", "https://example.com/cy", ["--source", "scraped_linkedin"])[0], 1)

    def test_mark_stopped_sets_opt_out_and_removes_from_contactable(self):
        self.add("Ada", "https://example.com/a")
        self.add("Bo", "https://example.com/b")
        self.assertEqual(run_main(pr, ["mark"] + self.args + ["P001", "stopped"])[0], 0)
        self.assertEqual(read_csv(self.path)[0]["opt_out"], "yes")
        _, out, _ = run_main(pr, ["contactable"] + self.args)
        self.assertNotIn("P001", out)
        self.assertIn("P002", out)
        code, out, _ = run_main(pr, ["mark"] + self.args + ["P001", "contacted"])
        self.assertEqual(code, 1)
        self.assertEqual(run_main(pr, ["mark"] + self.args + ["P002", "flying"])[0], 1)

    def test_stats_by_source_and_status(self):
        self.add("Ada", "https://example.com/a")
        self.add("Bo", "https://example.com/b", ["--source", "github"])
        _, out, _ = run_main(pr, ["stats"] + self.args)
        self.assertIn("google_search", out)
        self.assertIn("github", out)
        self.assertIn("not_contacted", out)
        self.assertIn("Contactable now", out)

    def test_import_text_file_of_lines_and_urls(self):
        text = self.tmp / "paste.txt"
        text.write_text("# pasted\nhttps://example.com/p/1\nAda Example | Sales lead | Austin | https://example.com/p/2\n"
                        "Bo Example, https://example.com/p/3\nnot a url line\n", encoding="utf-8")
        code, out, _ = run_main(pr, ["import"] + self.args + [str(text)])
        self.assertEqual(code, 0)
        self.assertIn("Imported 3 new", out)
        rows = read_csv(self.path)
        self.assertEqual({r["public_url"] for r in rows}, {"https://example.com/p/1", "https://example.com/p/2", "https://example.com/p/3"})
        self.assertEqual([r["prospect_id"] for r in rows], ["P001", "P002", "P003"])
        code, out, _ = run_main(pr, ["import"] + self.args + [str(text)])
        self.assertIn("skipped 3 duplicates", out)

    def test_import_csv_refuses_rows_with_emails_and_duplicates(self):
        sheet = self.tmp / "in.csv"
        sheet.write_text("name,url,headline,location,email\nAda,https://example.com/a,Lead,Austin,\n"
                         "Bo,https://example.com/b,Lead,Austin,bo@example.com\nAda,https://example.com/a,Lead,Austin,\n", encoding="utf-8")
        code, out, _ = run_main(pr, ["import"] + self.args + [str(sheet), "--source", "board_export"])
        self.assertEqual(code, 0)
        self.assertIn("Imported 1 new, skipped 1 duplicates, refused 1", out)
        self.assertEqual(read_csv(self.path)[0]["source"], "board_export")

    def test_reimport_never_resurrects_an_opted_out_person(self):
        self.add("Ada", "https://example.com/a")
        run_main(pr, ["mark"] + self.args + ["P001", "stopped"])
        self.add("Ada", "https://example.com/a")
        self.assertEqual(read_csv(self.path)[0]["opt_out"], "yes")
        self.assertEqual(len(read_csv(self.path)), 1)


class FormScriptTests(unittest.TestCase):
    def form(self):
        return {"title": "Apply: Bookkeeper", "description": "Short form, about 10 minutes.",
                "sections": [
                    {"title": "About you", "description": "Basics", "questions": [
                        {"text": "Your full name", "type": "short_text", "required": True},
                        {"text": "Email", "type": "email", "required": True},
                        {"text": "Portfolio link", "type": "url"}]},
                    {"title": "Your work", "questions": [
                        {"text": "Describe a reconciliation you did", "type": "paragraph", "required": True},
                        {"text": "Which tools have you used?", "type": "checkbox", "options": ["Excel", "QuickBooks"]},
                        {"text": "Can you start within a month?", "type": "multiple_choice", "options": ["Yes", "No"]},
                        {"text": "Upload your CV", "type": "file_upload"}]}]}

    def test_script_contains_expected_apps_script_calls(self):
        script = mfs.generate(self.form())
        for needle in ("FormApp.create(", "addTextItem()", "addParagraphTextItem()", "addMultipleChoiceItem()",
                       "addCheckboxItem()", "addPageBreakItem()", "addSectionHeaderItem()", "setChoiceValues(",
                       "requireTextIsEmail()", "requireTextIsUrl()", "SpreadsheetApp.create(",
                       "form.setDestination(FormApp.DestinationType.SPREADSHEET"):
            self.assertIn(needle, script)
        self.assertIn("function createApplicationForm()", script)

    def test_file_upload_becomes_a_link_question_with_a_comment(self):
        script = mfs.generate(self.form())
        self.assertIn("cannot create file upload questions", script)
        self.assertIn("paste a link to the file", script)

    def test_required_flag_and_string_escaping(self):
        form = {"title": 'Say "hi"', "questions": [{"text": 'Why "us"?\nTell us', "type": "short_text", "required": True}]}
        script = mfs.generate(form)
        self.assertIn('setTitle("Why \\"us\\"?\\nTell us").setRequired(true)', script)
        self.assertIn('FormApp.create("Say \\"hi\\"")', script)

    def test_script_is_balanced_javascript(self):
        script = mfs.generate(self.form())
        stripped = re.sub(r'"(?:[^"\\]|\\.)*"', '""', re.sub(r"//[^\n]*", "", script))
        stripped = re.sub(r"'[^'\n]*'", "''", stripped)
        for open_c, close_c in ("()", "{}", "[]"):
            self.assertEqual(stripped.count(open_c), stripped.count(close_c), open_c)
        for line in script.splitlines():
            if line.strip() and not line.strip().startswith("//") and not line.strip().endswith(("{", "}")):
                self.assertTrue(line.rstrip().endswith(";"), line)

    def test_validation_catches_problems(self):
        self.assertTrue(mfs.validate({}))
        self.assertTrue(mfs.validate({"title": "T", "questions": []}))
        self.assertTrue(mfs.validate({"title": "T", "questions": [{"text": "x", "type": "slider"}]}))
        self.assertTrue(mfs.validate({"title": "T", "questions": [{"text": "x", "type": "checkbox", "options": ["one"]}]}))
        self.assertEqual(mfs.validate({"title": "T", "questions": [{"text": "x", "type": "short_text"}]}), [])

    def test_flat_questions_shape_works(self):
        script = mfs.generate({"title": "T", "questions": [{"question": "Name?", "type": "short_text"}]})
        self.assertIn('setTitle("Name?")', script)
        self.assertNotIn("addSectionHeaderItem", script)

    def test_protected_trait_questions_get_a_warning(self):
        warnings = mfs.risky_warnings({"title": "T", "questions": [{"text": "What is your date of birth?"},
                                                                    {"text": "Your gender"}, {"text": "Describe your work"}]})
        self.assertEqual(len(warnings), 2)

    def test_cli_writes_gs_file_and_reports_bad_json(self):
        with TempDir() as tmp:
            source = tmp / "form.json"
            source.write_text(json.dumps(self.form()), encoding="utf-8")
            out = tmp / "create.gs"
            code, text, _ = run_main(mfs, [str(source), "--out", str(out)])
            self.assertEqual(code, 0)
            self.assertIn("FormApp.create", out.read_text(encoding="utf-8"))
            broken = tmp / "broken.json"
            broken.write_text("{", encoding="utf-8")
            self.assertEqual(run_main(mfs, [str(broken)])[0], 1)
            self.assertEqual(run_main(mfs, [str(tmp / "missing.json")])[0], 1)

    def test_vars_fill_placeholders_and_leftovers_are_warned(self):
        form = {"title": "{{company_name}} application", "description": "Write to {{contact_email}}",
                "questions": [{"label": "Name", "type": "short_text"}]}
        filled = mfs.fill_vars(form, {"company_name": "Northlight"})
        self.assertEqual(filled["title"], "Northlight application")
        self.assertEqual(mfs.unfilled_placeholders(filled), ["contact_email"])
        with TempDir() as tmp:
            source, values = tmp / "f.json", tmp / "v.json"
            source.write_text(json.dumps(form), encoding="utf-8")
            values.write_text(json.dumps({"company_name": "Northlight"}), encoding="utf-8")
            code, text, err = run_main(mfs, [str(source), "--vars", str(values)])
            self.assertEqual(code, 0)
            self.assertIn("Northlight application", text)
            self.assertIn("contact_email", err)

    def test_real_form_template_when_present(self):
        path = ROOT / "templates" / "forms" / "application-form.json"
        if not path.exists():
            self.skipTest("templates/forms/application-form.json not present yet")
        form = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(mfs.validate(form), [])
        self.assertIn("FormApp.create", mfs.generate(form))


if __name__ == "__main__":
    unittest.main()
