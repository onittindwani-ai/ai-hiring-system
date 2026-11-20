"""Kit linter: checks the repo itself before it is shared.

Usage:
    python3 tools/lint_kit.py
    python3 tools/lint_kit.py --root /path/to/ai-hiring-system
    python3 tools/lint_kit.py --links

What it does:
    Scans every text file in the kit and prints one line per problem, then exits 1 if there are any.
    Checks: no em dash or en dash (or look alikes) anywhere; no personal computer paths; nothing that
    looks like a secret key or a private storage link; internal markdown links point at files that
    exist; every .claude/skills/<name>/SKILL.md starts with frontmatter that has name and description.
    With --links it also lists web links outside the short allowed list. The hiring/ folder (your
    private candidate data) is skipped. Use lint(root) from Python to get the problems as a list.
"""
import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

TEXT_SUFFIXES = {".md", ".py", ".json", ".jsonl", ".csv", ".txt", ".yml", ".yaml", ".gs", ".js", ".jsonld", ".toml", ".cfg"}
TEXT_NAMES = {".gitignore", ".env.example", "LICENSE", ".gitkeep"}
SKIP_DIRS = {".git", "__pycache__", "node_modules", "hiring", ".venv", ".pytest_cache"}
MAX_BYTES = 2_000_000

# Built from pieces so this file does not trip its own checks.
DASH_CHARS = {"\u2012": "figure dash", "\u2013": "en dash", "\u2014": "em dash", "\u2015": "horizontal bar", "\u2212": "minus sign"}
LOCAL_PATH = "/Us" + "ers/"
SECRET_PATTERNS = [
    ("an API style key (sk-)", re.compile(r"\bsk-[A-Za-z0-9_]{20,}")),
    ("an AWS key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("a GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("a Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("a Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}")),
    ("a private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]
KEY_LINE_RE = re.compile(r"TYPESAFE_API_KEY\s*=\s*['\"]?([A-Za-z0-9_\-]{12,})")
PLACEHOLDER_WORDS = ("your", "here", "paste", "example", "placeholder", "xxxx", "changeme")
PRIVATE_HOSTS = ["drive.google" + ".com", "docs.google" + ".com", "notion" + ".so", "notion" + ".site"]
ALLOWED_HOST_SUFFIXES = ["typesafe.ai", "chromewebstore.google.com", "support.claude.com", "code.claude.com",
                         "eeoc.gov", "nyc.gov", "eur-lex.europa.eu", "leg.colorado.gov", "ilga.gov",
                         "calcivilrights.ca.gov", "example.com", "example.org"]
ALLOWED_URL_PREFIXES = ["https://github.com/onittindwani-ai/ai-hiring-system"]

LINK_RE = re.compile(r"(?<!!)\[[^\]\n]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
URL_RE = re.compile(r"https?://[^\s)>\]\"'`]+")
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def iter_text_files(root):
    for path in sorted(Path(root).rglob("*")):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_NAMES:
            if path.stat().st_size <= MAX_BYTES:
                yield path


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def check_text(rel, text):
    problems = []
    for number, line in enumerate(text.splitlines(), start=1):
        for char, name in DASH_CHARS.items():
            if char in line:
                problems.append("%s:%d: contains an %s. Use a comma, colon, period or parentheses." % (rel, number, name))
        if LOCAL_PATH in line:
            problems.append("%s:%d: contains a personal computer path." % (rel, number))
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                problems.append("%s:%d: looks like %s. Remove it and rotate the key if it was real." % (rel, number, label))
        key_match = KEY_LINE_RE.search(line)
        if key_match and not any(w in key_match.group(1).lower() for w in PLACEHOLDER_WORDS):
            problems.append("%s:%d: looks like a filled TYPESAFE_API_KEY. Remove it and rotate the key if it was real." % (rel, number))
        lowered = line.lower()
        for host in PRIVATE_HOSTS:
            if host in lowered:
                problems.append("%s:%d: contains a private storage or notes link (%s)." % (rel, number, host))
    return problems


def check_links(root, path, text):
    problems = []
    prose = INLINE_CODE_RE.sub("", FENCE_RE.sub("", text))
    for target in LINK_RE.findall(prose):
        if re.match(r"^(https?:|mailto:|#)", target):
            continue
        clean = target.split("#", 1)[0]
        if clean and not (path.parent / clean).exists():
            problems.append("%s: link to %s does not exist." % (path.relative_to(root), target))
    return problems


def check_skill(root, path, text):
    rel = path.relative_to(root)
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    if not match:
        return ["%s: SKILL.md needs frontmatter (--- name and description ---) at the top." % rel]
    block = match.group(1)
    return ["%s: frontmatter is missing %s." % (rel, field) for field in ("name", "description")
            if not re.search(r"^%s:\s*\S" % field, block, re.MULTILINE)]


def check_external_links(rel, text):
    problems = []
    for url in URL_RE.findall(text):
        url = url.rstrip(".,;:")
        host = (urlparse(url).hostname or "").lower()
        if any(url.startswith(p) for p in ALLOWED_URL_PREFIXES):
            continue
        if any(host == s or host.endswith("." + s) for s in ALLOWED_HOST_SUFFIXES):
            continue
        problems.append("%s: link outside the allowed list: %s" % (rel, url))
    return problems


def lint(root, links=False):
    """Return a list of problem strings. An empty list means the kit is clean."""
    root = Path(root)
    problems = []
    for path in iter_text_files(root):
        text = read_text(path)
        if text is None:
            continue
        rel = path.relative_to(root)
        problems += check_text(rel, text)
        if path.suffix.lower() == ".md":
            problems += check_links(root, path, text)
        if path.name == "SKILL.md" and ".claude" in path.parts and "skills" in path.parts:
            problems += check_skill(root, path, text)
        if links:
            problems += check_external_links(rel, text)
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description="Lint the hiring kit")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--links", action="store_true", help="also list web links outside the allowed list")
    args = parser.parse_args(argv)
    problems = lint(args.root, args.links)
    if not problems:
        print("OK: no problems found.")
        return 0
    for problem in problems:
        print(problem)
    print("%d problem(s)." % len(problems))
    return 1


if __name__ == "__main__":
    sys.exit(main())
