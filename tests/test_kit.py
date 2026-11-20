"""Kit level tests: counts match the README, skills and commands are well formed,
docs exist, links resolve, no dashes, no private paths, no secrets.

Usage:
    python3 -m unittest tests.test_kit
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_SUFFIXES = {".md", ".json", ".jsonl", ".jsonld", ".py", ".txt", ".yml", ".yaml", ".example", ".csv", ".gs"}
SKIP_DIRS = {".git", "__pycache__", "hiring"}
DASHES = (chr(0x2013), chr(0x2014))


def text_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix in TEXT_SUFFIXES or path.name in {".gitignore", ".env.example", "LICENSE"}:
            yield path


def count_files(folder, pattern):
    return len(list((ROOT / folder).glob(pattern)))


def readme_counts():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    match = re.search(r"<!-- counts: ([^>]*?) -->", text)
    assert match, "README.md needs a counts comment"
    return {key: int(value) for key, value in (item.split("=") for item in match.group(1).split())}


class CountsTest(unittest.TestCase):
    def test_readme_counts_match_reality(self):
        counts = readme_counts()
        actual = {
            "skills": count_files(".claude/skills", "*/SKILL.md"),
            "commands": count_files(".claude/commands", "*.md"),
            "scorecards": count_files("templates/scorecards", "*.json"),
            "messages": count_files("templates/messages", "*.md"),
            "knowledge": count_files("docs/knowledge", "*.md"),
            "candidates": sum(1 for line in (ROOT / "data/sample/candidates.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()),
        }
        self.assertEqual(counts, actual)

    def test_minimum_counts(self):
        self.assertGreaterEqual(count_files(".claude/skills", "*/SKILL.md"), 10)
        self.assertEqual(count_files(".claude/commands", "*.md"), 8)
        self.assertEqual(count_files("templates/scorecards", "*.json"), 12)
        self.assertEqual(count_files("templates/messages", "*.md"), 20)
        self.assertEqual(count_files("docs/knowledge", "*.md"), 14)


class SkillsAndCommandsTest(unittest.TestCase):
    def test_every_skill_has_frontmatter(self):
        for path in (ROOT / ".claude/skills").glob("*/SKILL.md"):
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), path)
            head = text.split("---", 2)[1]
            self.assertIn("name: " + path.parent.name, head, path)
            self.assertRegex(head, r"description: .{40,}", path)

    def test_every_command_has_description(self):
        for path in (ROOT / ".claude/commands").glob("*.md"):
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\ndescription: "), path)

    def test_skills_reference_real_tools_and_docs(self):
        pattern = re.compile(r"(tools/[a-z_]+\.py|docs/[A-Za-z0-9_/\-]+\.md|templates/[A-Za-z0-9_/\-]+\.(?:md|json))")
        missing = []
        for path in list((ROOT / ".claude").rglob("*.md")) + [ROOT / "CLAUDE.md"]:
            for ref in pattern.findall(path.read_text(encoding="utf-8")):
                if "<" in ref or "*" in ref:
                    continue
                if not (ROOT / ref).exists():
                    missing.append((path.name, ref))
        self.assertEqual(missing, [])


class HygieneTest(unittest.TestCase):
    def test_no_em_or_en_dashes(self):
        bad = [str(p.relative_to(ROOT)) for p in text_files() if any(d in p.read_text(encoding="utf-8", errors="replace") for d in DASHES)]
        self.assertEqual(bad, [])

    def test_no_private_paths_or_links(self):
        bad = []
        for path in text_files():
            if path.name == "test_kit.py":
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for needle in ("/" + "Users/", "drive." + "google.com", "docs." + "google.com", "notion." + "so"):
                if needle in text:
                    bad.append((str(path.relative_to(ROOT)), needle))
        self.assertEqual(bad, [])

    def test_no_secret_looking_strings(self):
        patterns = [re.compile(r"sk-[A-Za-z0-9]{20,}"), re.compile(r"ghp_[A-Za-z0-9]{20,}"), re.compile(r"gho_[A-Za-z0-9]{20,}"),
                    re.compile(r"AKIA[0-9A-Z]{16}"), re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")]
        bad = []
        for path in text_files():
            text = path.read_text(encoding="utf-8", errors="replace")
            for pattern in patterns:
                if pattern.search(text):
                    bad.append(str(path.relative_to(ROOT)))
        self.assertEqual(bad, [])

    def test_internal_markdown_links_resolve(self):
        link = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
        bad = []
        for path in ROOT.rglob("*.md"):
            if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
                continue
            for target in link.findall(path.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "mailto:")):
                    continue
                if not (path.parent / target).exists():
                    bad.append((str(path.relative_to(ROOT)), target))
        self.assertEqual(bad, [])

    def test_gitignore_protects_private_files(self):
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for needle in (".env", "config/profile.json", "hiring/*"):
            self.assertIn(needle, text)

    def test_only_allowed_hosts_in_links(self):
        allowed = ("typesafe.ai", "docs.typesafe.ai", "console.typesafe.ai", "chromewebstore.google.com", "support.claude.com",
                   "code.claude.com", "github.com/onittindwani-ai/ai-hiring-system", "api.typesafe.ai", "example.com", "example.org",
                   "schema.org", "python.org", "script.google.com", "eeoc.gov", "nyc.gov", "eur-lex.europa.eu", "leg.colorado.gov",
                   "ilga.gov", "calcivilrights.ca.gov", "linkedin.com", "127.0.0.1", "localhost", "claude.ai", "tally.so", "forms.google.com",
                   "europa.eu", "ico.org.uk", "dol.gov", "gov.uk", "indeed.com", "naukri.com", "wellfound.com", "github.com", "gdpr.eu", "ca.gov", "colorado.gov", "ftc.gov")
        url = re.compile(r"https?://([A-Za-z0-9.\-]+)")
        bad = set()
        for path in text_files():
            if path.suffix in {".py", ".jsonl"} or path.name == "test_kit.py":
                continue
            for host in url.findall(path.read_text(encoding="utf-8", errors="replace")):
                if not any(host == a or host.endswith("." + a) or a.startswith(host) for a in allowed):
                    bad.add((str(path.relative_to(ROOT)), host))
        self.assertEqual(sorted(bad), [])


class DataFilesTest(unittest.TestCase):
    def test_json_files_parse(self):
        for path in text_files():
            if path.suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
