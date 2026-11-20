"""Example 5: the weekly pipeline review on a made up pipeline.

Usage:
    python3 examples/05_weekly_review.py

What it does:
    Builds a fake pipeline.csv in a temporary folder (14 made up people, fixed dates), then runs the
    real tools/pipeline.py stats and weekly commands and prints the weekly report: counts per stage,
    where people leak out, who is stuck, and one next action per stuck person. Everything is
    invented for practice. Nothing is sent. No network and no key. The temporary folder is removed.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from hlib import PIPELINE_COLUMNS, write_csv  # noqa: E402

TODAY = "2026-12-14"

PEOPLE = [
    ("P01", "Alex Example", "applied", "2026-12-12", "form", "", "Screen against the scorecard", "2026-12-15", ""),
    ("P02", "Bea Example", "applied", "2026-12-01", "form", "", "", "", ""),
    ("P03", "Chen Example", "screened", "2026-12-03", "form", "81.5", "Owner decides", "2026-12-08", ""),
    ("P04", "Dara Example", "screened", "2026-12-11", "board_export", "58.0", "", "", ""),
    ("P05", "Eli Example", "shortlisted", "2026-11-28", "sourced", "77.0", "Draft invitation", "2026-12-02", ""),
    ("P06", "Faye Example", "contacted", "2026-12-02", "sourced", "74.5", "Follow up once", "2026-12-09", ""),
    ("P07", "Gus Example", "replied", "2026-12-10", "referral", "79.0", "Offer two times", "2026-12-12", ""),
    ("P08", "Hana Example", "interview_scheduled", "2026-12-09", "form", "83.0", "Confirm the time", "2026-12-15", ""),
    ("P09", "Ivo Example", "interviewed", "2026-12-04", "form", "76.0", "Fill the rating sheet", "2026-12-07", ""),
    ("P10", "Jun Example", "work_sample", "2026-12-08", "referral", "85.5", "Score the sample", "2026-12-12", ""),
    ("P11", "Kai Example", "offer", "2026-12-06", "form", "88.0", "Ask what is still open", "2026-12-10", ""),
    ("P12", "Lia Example", "rejected", "2026-12-05", "form", "49.0", "", "", "last_active:screened"),
    ("P13", "Max Example", "withdrawn", "2026-12-07", "sourced", "72.0", "", "", "last_active:contacted"),
    ("P14", "Noa Example", "hired", "2026-12-01", "referral", "90.0", "", "", ""),
]


def run(*args):
    result = subprocess.run([sys.executable, str(ROOT / "tools" / "pipeline.py"), *args],
                            capture_output=True, text=True, cwd=str(ROOT))
    if result.returncode != 0:
        raise SystemExit(result.stdout + result.stderr)
    return result.stdout


def main():
    with tempfile.TemporaryDirectory() as tmp:
        role_dir = Path(tmp) / "support-specialist"
        role_dir.mkdir()
        csv_path = role_dir / "pipeline.csv"
        rows = [dict(zip(PIPELINE_COLUMNS, person)) for person in PEOPLE]
        write_csv(csv_path, PIPELINE_COLUMNS, rows)
        print("A made up pipeline of %d people, as of %s.\n" % (len(rows), TODAY))
        print(run("stats", "--role", "support-specialist", "--base", tmp, "--today", TODAY))
        out = role_dir / "WEEKLY.md"
        print(run("weekly", "--role", "support-specialist", "--base", tmp, "--today", TODAY, "--out", str(out)))
        print("--- WEEKLY.md ---")
        print(out.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
