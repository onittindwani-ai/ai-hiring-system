"""Tests for check_setup.py, new_role.py and lint_kit.py (self contained, use temp folders)."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hiring_fixtures import ROOT, TempDir, make_scorecard, run_main  # noqa: E402

import check_setup as cs  # noqa: E402
import lint_kit as lk  # noqa: E402
import new_role as nr  # noqa: E402
from hlib import PIPELINE_COLUMNS, PROSPECT_COLUMNS, read_csv  # noqa: E402

# Built at run time so this test file itself stays clean under the linter.
EM = "\u2014"
FAKE_KEY = "sk-" + "a1b2c3d4" * 4
FAKE_TYPESAFE = "TYPESAFE_API_KEY=" + "Zq8rT2" * 4
LOCAL = "/Us" + "ers/someone/file"
DRIVE = "https://drive.google" + ".com/file/d/abc"


def write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class CheckSetupTests(unittest.TestCase):
    def test_never_prints_a_key_value(self):
        with TempDir() as tmp:
            write(tmp, ".env", "TYPESAFE_API_KEY=%s\n" % "supersecretvalue123456")
            report = cs.build_report(tmp, include_jev=True, environ={})
            self.assertNotIn("supersecretvalue123456", report)
            self.assertIn("TYPESAFE_API_KEY: set (in the .env)", report)
            report_env = cs.build_report(tmp, True, environ={"TYPESAFE_API_KEY": "anothersecret999"})
            self.assertNotIn("anothersecret999", report_env)
            self.assertIn("set (in the environment)", report_env)

    def test_not_set_when_missing_or_empty(self):
        with TempDir() as tmp:
            self.assertIn("not set", cs.build_report(tmp, environ={}))
            write(tmp, ".env", "TYPESAFE_API_KEY=\n# TYPESAFE_API_KEY=commented\n")
            self.assertIn("TYPESAFE_API_KEY: not set", cs.build_report(tmp, environ={}))

    def test_profile_states(self):
        with TempDir() as tmp:
            self.assertIn("not created yet", cs.profile_state(tmp)[0])
            write(tmp, "config/profile.json", "{")
            self.assertIn("not valid JSON", cs.profile_state(tmp)[0])
            write(tmp, "config/profile.json", json.dumps({"setup_done": False, "company_name": "", "country": "Spain"}))
            state, empty = cs.profile_state(tmp)
            self.assertIn("setup_done is false", state)
            self.assertIn("2 of 3 fields filled", state)
            self.assertEqual(empty, ["company_name"])
            write(tmp, "config/profile.json", json.dumps({"setup_done": True, "company_name": "Northlight"}))
            self.assertIn("setup_done is true", cs.profile_state(tmp)[0])
            self.assertNotIn("Northlight", cs.build_report(tmp, environ={}))  # values are not printed

    def test_jev_section_is_friendly_and_optional(self):
        with TempDir() as tmp:
            text = " ".join(cs.build_report(tmp, include_jev=True, environ={}).split())
            self.assertIn("OPTIONAL", text)
            self.assertIn("works fully without it", text)
            self.assertIn("https://console.typesafe.ai/keys", text)
            self.assertIn("not made or endorsed by TypeSafe AI", text)
            self.assertNotIn("JEV (OPTIONAL)", cs.build_report(tmp, environ={}))
            fake = cs.build_report(tmp, include_jev=True, environ={"JEV_BASE_URL": "http://127.0.0.1:8099"})
            self.assertIn("JEV_BASE_URL is set", fake)

    def test_old_python_is_called_out_and_missing_files_listed(self):
        with TempDir() as tmp:
            text = cs.build_report(tmp, environ={}, python_version=(3, 8, 0))
            self.assertIn("too old", text)
            self.assertIn("missing:", text)
            self.assertIn("README.md", text)

    def test_cli_always_exits_zero(self):
        with TempDir() as tmp:
            code, out, _ = run_main(cs, ["--root", str(tmp), "--jev"])
            self.assertEqual(code, 0)
            self.assertIn("SETUP CHECK", out)

    def test_runs_on_the_real_kit(self):
        code, out, _ = run_main(cs, ["--jev"])
        self.assertEqual(code, 0)
        self.assertNotIn(os.environ.get("TYPESAFE_API_KEY", "\0not-a-key"), out)


class NewRoleTests(unittest.TestCase):
    def test_scaffold_creates_everything(self):
        with TempDir() as tmp:
            folder = nr.scaffold("Sales Development Rep!", str(tmp / "hiring"))
            self.assertEqual(folder.name, "sales-development-rep")
            for name in ("inbox", "candidates", "drafts"):
                self.assertTrue((folder / name).is_dir())
            self.assertTrue((folder / "plan.md").exists())
            self.assertEqual((folder / "prospects.csv").read_text(encoding="utf-8").strip(), ",".join(PROSPECT_COLUMNS))
            self.assertEqual((folder / "pipeline.csv").read_text(encoding="utf-8").strip(), ",".join(PIPELINE_COLUMNS))
            self.assertEqual(json.loads((folder / "scorecard.json").read_text(encoding="utf-8"))["role_id"], "sales-development-rep")
            self.assertEqual(read_csv(folder / "pipeline.csv"), [])

    def test_scorecard_is_copied_and_plan_uses_its_title(self):
        with TempDir() as tmp:
            card = tmp / "card.json"
            card.write_text(json.dumps(make_scorecard()), encoding="utf-8")
            folder = nr.scaffold("sdr", str(tmp / "hiring"), str(card))
            self.assertEqual(json.loads((folder / "scorecard.json").read_text(encoding="utf-8"))["title"], "Sales Development Rep")
            plan = (folder / "plan.md").read_text(encoding="utf-8")
            self.assertIn("Sales Development Rep", plan)
            self.assertIn("hiring/sdr/scorecard.json", plan)

    def test_existing_folder_is_never_touched(self):
        with TempDir() as tmp:
            folder = nr.scaffold("bookkeeper", str(tmp / "hiring"))
            marker = folder / "plan.md"
            marker.write_text("mine", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                nr.scaffold("bookkeeper", str(tmp / "hiring"))
            self.assertEqual(marker.read_text(encoding="utf-8"), "mine")

    def test_cli_errors_are_friendly(self):
        with TempDir() as tmp:
            self.assertEqual(run_main(nr, ["!!!", "--base", str(tmp)])[0], 1)
            code, out, _ = run_main(nr, ["x", "--base", str(tmp), "--scorecard", str(tmp / "no.json")])
            self.assertEqual(code, 1)
            self.assertIn("Scorecard not found", out)
            self.assertFalse((tmp / "x").exists())
            self.assertEqual(run_main(nr, ["ok-role", "--base", str(tmp)])[0], 0)
            code, out, _ = run_main(nr, ["ok-role", "--base", str(tmp)])
            self.assertEqual(code, 1)
            self.assertIn("did not touch it", out)


class LintTests(unittest.TestCase):
    def kit(self, tmp):
        write(tmp, "README.md", "# Kit\n\nSee [guide](docs/guide.md) and [web](https://example.com/x).\n")
        write(tmp, "docs/guide.md", "# Guide\n\nBack to [readme](../README.md#top).\n")
        write(tmp, ".claude/skills/hiring-start/SKILL.md", "---\nname: hiring-start\ndescription: Starts a hire\n---\n\nBody\n")
        return tmp

    def test_clean_kit_has_no_problems(self):
        with TempDir() as tmp:
            self.assertEqual(lk.lint(self.kit(tmp)), [])
            code, out, _ = run_main(lk, ["--root", str(tmp)])
            self.assertEqual(code, 0)
            self.assertIn("OK", out)

    def test_dashes_are_found_with_line_numbers(self):
        with TempDir() as tmp:
            write(self.kit(tmp), "docs/bad.md", "Fine line\nBad %s line\n" % EM)
            problems = lk.lint(tmp)
            self.assertEqual(len(problems), 1)
            self.assertIn("docs/bad.md:2", problems[0])
            self.assertIn("em dash", problems[0])
            self.assertEqual(run_main(lk, ["--root", str(tmp)])[0], 1)

    def test_local_paths_secrets_and_private_links(self):
        with TempDir() as tmp:
            self.kit(tmp)
            write(tmp, "a.txt", "path %s\n" % LOCAL)
            write(tmp, "b.py", 'KEY = "%s"\n' % FAKE_KEY)
            write(tmp, "c.md", "link %s\n" % DRIVE)
            write(tmp, "d.txt", FAKE_TYPESAFE + "\n")
            text = "\n".join(lk.lint(tmp))
            self.assertIn("a.txt:1: contains a personal computer path", text)
            self.assertIn("b.py:1: looks like an API style key", text)
            self.assertIn("private storage or notes link", text)
            self.assertIn("d.txt:1: looks like a filled TYPESAFE_API_KEY", text)

    def test_empty_or_placeholder_key_lines_are_fine(self):
        with TempDir() as tmp:
            self.kit(tmp)
            write(tmp, ".env.example", "TYPESAFE_API_KEY=\n")
            write(tmp, "notes.md", "Set TYPESAFE_API_KEY=your_key_here in .env\n")
            self.assertEqual(lk.lint(tmp), [])

    def test_broken_internal_links_are_found_but_code_and_web_links_skipped(self):
        with TempDir() as tmp:
            self.kit(tmp)
            write(tmp, "docs/links.md", "[gone](missing.md) and [ok](guide.md#x)\n```\n[example](nowhere.md)\n```\n`[inline](nope.md)`\n![img](none.png)\n")
            problems = lk.lint(tmp)
            self.assertEqual(len(problems), 1)
            self.assertIn("link to missing.md does not exist", problems[0])

    def test_skill_frontmatter_rules(self):
        with TempDir() as tmp:
            self.kit(tmp)
            write(tmp, ".claude/skills/none/SKILL.md", "no frontmatter here\n")
            write(tmp, ".claude/skills/partial/SKILL.md", "---\nname: partial\n---\nBody\n")
            text = "\n".join(lk.lint(tmp))
            self.assertIn("none/SKILL.md: SKILL.md needs frontmatter", text)
            self.assertIn("partial/SKILL.md: frontmatter is missing description", text)
            self.assertNotIn("hiring-start", text)

    def test_hiring_folder_and_git_are_skipped(self):
        with TempDir() as tmp:
            self.kit(tmp)
            write(tmp, "hiring/role/candidates/a.json", "bad %s dash" % EM)
            write(tmp, ".git/config", "bad %s" % EM)
            self.assertEqual(lk.lint(tmp), [])

    def test_external_link_check_is_opt_in(self):
        with TempDir() as tmp:
            self.kit(tmp)
            write(tmp, "docs/web.md", "https://random-site.net/page and https://docs.typesafe.ai and "
                  "https://github.com/onittindwani-ai/ai-hiring-system\n")
            self.assertEqual(lk.lint(tmp), [])
            problems = lk.lint(tmp, links=True)
            self.assertEqual(len(problems), 1)
            self.assertIn("random-site.net", problems[0])

    def test_the_tools_and_tests_of_this_kit_are_clean(self):
        # Only lint files this agent wrote, so the test does not depend on other agents' work being finished.
        names = ["make_search_strings", "prospects", "pipeline", "funnel_calculator", "budget_planner", "make_form_script",
                 "interview_kit", "message_check", "render_message", "check_setup", "new_role", "lint_kit"]
        with TempDir() as tmp:
            for name in names:
                write(tmp, "tools/%s.py" % name, (ROOT / "tools" / ("%s.py" % name)).read_text(encoding="utf-8"))
            for name in ("test_planning_tools", "test_sourcing_tools", "test_message_tools", "test_setup_and_lint", "hiring_fixtures"):
                write(tmp, "tests/%s.py" % name, (ROOT / "tests" / ("%s.py" % name)).read_text(encoding="utf-8"))
            self.assertEqual(lk.lint(tmp), [])
            for name in names:
                text = (ROOT / "tools" / ("%s.py" % name)).read_text(encoding="utf-8")
                self.assertIn("Usage:", text, name)
                self.assertTrue(text.startswith('"""'), name)

    def test_whole_kit_is_clean_when_everything_is_in_place(self):
        if not (ROOT / "README.md").exists() or not (ROOT / "templates").exists():
            self.skipTest("the rest of the kit is not written yet")
        problems = lk.lint(ROOT)
        self.assertEqual(problems, [], "\n".join(problems[:20]))


if __name__ == "__main__":
    unittest.main()
