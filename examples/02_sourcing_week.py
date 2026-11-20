"""Example 2: a sourcing week, offline: search strings, then a prospect list round trip.

Usage:
    python3 examples/02_sourcing_week.py

What it does:
    1. Builds search strings for the made up Sales Development Rep role (tools/make_search_strings.py)
       and shows which ones Claude may run (public Google results) and which ones YOU run in your own account.
    2. Starts a prospect list in a temporary folder, adds one person by hand, imports a pasted text list
       of made up people (one person is listed twice, the import skips the repeat), marks one person as stopped, and lists who
       is still contactable. A stopped or opted out person is never contactable.
    Everything is invented. Nothing is searched, sent or saved outside the temporary folder.
    No network and no key.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROLE = "sales-development-rep"

PASTED_LIST = """\
Rosa Example | SDR at a roofing company, writes short cold emails | Leeds | https://example.com/in/rosa-example
Tomas Example | Appointment setter for window cleaners | Leeds | https://example.com/in/tomas-example
Rosa Example | SDR at a roofing company, writes short cold emails | Leeds | https://example.com/in/rosa-example
Sam Example | Customer success, moving into outbound | Manchester | https://example.org/sam-example
"""


def run(script, *args):
    result = subprocess.run([sys.executable, str(ROOT / "tools" / script), *args],
                            capture_output=True, text=True, cwd=str(ROOT))
    if result.returncode != 0:
        raise SystemExit("%s failed:\n%s" % (script, result.stdout + result.stderr))
    return result.stdout.strip()


def main():
    scorecard = str(ROOT / "data" / "sample" / "scorecard-sales-development-rep.json")
    print("STEP 1: search strings (nothing has been run)\n")
    strings = run("make_search_strings.py", scorecard, "--location", "Leeds")
    for line in strings.splitlines():
        if line.startswith("## ") or line.startswith("Who runs it"):
            print(line)
    print()

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "hiring"
        print("STEP 2: a prospect list round trip in a temporary folder\n")
        print(run("prospects.py", "init", ROLE, "--base", str(base)))
        print(run("prospects.py", "add", "--role", ROLE, "--base", str(base), "--name", "Ana Example",
                  "--url", "https://example.com/in/ana-example", "--headline", "Inside sales, home services",
                  "--location", "Leeds", "--source", "google_search",
                  "--fit-note", "Public profile shows weekly cold outreach to home service firms"))
        pasted = Path(tmp) / "pasted.txt"
        pasted.write_text(PASTED_LIST, encoding="utf-8")
        print(run("prospects.py", "import", "--role", ROLE, "--base", str(base), str(pasted), "--source", "google_search"))
        print(run("prospects.py", "dedupe", "--role", ROLE, "--base", str(base)))
        print(run("prospects.py", "stats", "--role", ROLE, "--base", str(base)))
        print()
        print("Tomas replied STOP, so he is marked stopped and will never be listed again:")
        print(run("prospects.py", "mark", "--role", ROLE, "--base", str(base), "P003", "stopped"))
        print()
        print("Who may still be contacted (by you, after you read and approve each message):")
        print(run("prospects.py", "contactable", "--role", ROLE, "--base", str(base)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
