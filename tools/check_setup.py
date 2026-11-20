"""Setup check: is this folder ready to use, and is the optional Jev connection set up?

Usage:
    python3 tools/check_setup.py
    python3 tools/check_setup.py --jev
    python3 tools/check_setup.py --root /path/to/ai-hiring-system

What it does:
    Prints a plain readiness report: Python version, the key files of the kit, the state of
    config/profile.json, and whether the Jev key exists. It NEVER prints a key or any secret
    value. It only says "set" or "not set" (and where). With --jev it adds a friendly section
    explaining the optional Jev connection and what to do next. It changes nothing and always
    exits 0, because a missing optional piece is not a failure.
"""
import argparse
import json
import os
import sys
from pathlib import Path

REQUIRED_FILES = ["README.md", "00-START-HERE.md", "01-SETUP.md", "02-QUICK-START-PROMPT.md", "CLAUDE.md",
                  "tools/hlib.py", "config/profile.example.json"]
REQUIRED_DIRS = [".claude/skills", "templates/scorecards", "docs/knowledge", "hiring"]
KEY_NAME = "TYPESAFE_API_KEY"
MIN_PYTHON = (3, 9)


def env_file_has_key(root, name=KEY_NAME):
    """True when .env has a non empty value for the key. The value itself is never returned."""
    path = Path(root) / ".env"
    if not path.exists():
        return False
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if key.strip() == name and value.strip().strip('"').strip("'"):
            return True
    return False


def key_status(root, environ=None):
    """Return ('environment' | '.env' | None). Never the value."""
    environ = os.environ if environ is None else environ
    if environ.get(KEY_NAME, "").strip():
        return "environment"
    if env_file_has_key(root):
        return ".env"
    return None


def profile_state(root):
    path = Path(root) / "config" / "profile.json"
    if not path.exists():
        return "not created yet (the start skill creates it with you)", []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "exists but is not valid JSON (fix or delete it, then run the start skill again)", []
    if not isinstance(data, dict):
        return "exists but is not a JSON object", []
    empty = sorted(k for k, v in data.items() if v in ("", None, [], {}))
    done = data.get("setup_done") is True
    state = "found, setup_done is %s, %d of %d fields filled" % ("true" if done else "false", len(data) - len(empty), len(data))
    return state, empty


def build_report(root, include_jev=False, environ=None, python_version=None):
    root = Path(root)
    version = python_version or sys.version_info[:3]
    lines = ["SETUP CHECK", "", "Folder: %s" % root.name, ""]
    ok_python = tuple(version[:2]) >= MIN_PYTHON
    lines.append("Python %d.%d.%d: %s" % (version[0], version[1], version[2],
                                         "OK" if ok_python else "too old, this kit needs Python 3.9 or newer"))
    missing = [f for f in REQUIRED_FILES if not (root / f).is_file()] + [d for d in REQUIRED_DIRS if not (root / d).is_dir()]
    lines.append("Kit files: %s" % ("all present" if not missing else "missing: " + ", ".join(missing)))
    state, empty = profile_state(root)
    lines.append("config/profile.json: %s" % state)
    if empty:
        lines.append("  empty fields: %s" % ", ".join(empty))
    where = key_status(root, environ)
    lines.append("%s: %s" % (KEY_NAME, ("set (in the %s)" % where) if where else "not set"))
    lines.append("Real candidate data folder (hiring/): %s" % ("present" if (root / "hiring").is_dir() else "missing"))
    if include_jev:
        lines += jev_section(where, environ)
    lines += ["", "Nothing was changed. Keys are never printed."]
    return "\n".join(lines)


def jev_section(where, environ=None):
    environ = os.environ if environ is None else environ
    lines = ["", "JEV (OPTIONAL)", "",
             "Jev is a fast scoring model from TypeSafe AI. This kit works fully without it. It only makes",
             "scoring faster and gives each answer a confidence number. This kit is independent and is not",
             "made or endorsed by TypeSafe AI."]
    if environ.get("JEV_BASE_URL", "").strip():
        lines.append("JEV_BASE_URL is set, so tools talk to that address (the offline fake, if you started tools/mock_jev.py).")
    if where:
        lines += ["", "Your key is set. Run: python3 tools/jev_check.py (one tiny request, costs very little)."]
    else:
        lines += ["", "No key yet. To try it, in your own terminal (never in the chat):",
                  "  1. Make an account at https://typesafe.ai and create a key at https://console.typesafe.ai/keys",
                  "     (on 2026-10-23 a new key needed a few dollars of credit first; billing rules can change, so expect to add some).",
                  "  2. Copy .env.example to .env and put the key after TYPESAFE_API_KEY=",
                  "  3. Run: python3 tools/check_setup.py --jev again.",
                  "Docs: https://docs.typesafe.ai. Practice offline first with the fake: python3 tools/mock_jev.py"]
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check that the hiring kit is ready")
    parser.add_argument("--jev", action="store_true", help="include the optional Jev section")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    args = parser.parse_args(argv)
    print(build_report(args.root, args.jev))
    return 0


if __name__ == "__main__":
    sys.exit(main())
