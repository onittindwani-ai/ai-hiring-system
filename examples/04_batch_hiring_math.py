"""Example 4: the maths of hiring five people into the same role.

Usage:
    python3 examples/04_batch_hiring_math.py
    python3 examples/04_batch_hiring_math.py --hires 8 --base-pay 52000

What it does:
    Runs the real funnel calculator and budget planner for a batch of identical hires and prints a
    plain summary: how many offers to make (some people say no), how many finalists, interviews and
    applicants you need, the warm backup list, and what finding five people costs by path.
    All numbers are STARTING ASSUMPTIONS printed by the tools, replace them with your own data.
    Nothing is sent, posted or saved. No network and no key.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run_json(script, *args):
    result = subprocess.run([sys.executable, str(ROOT / "tools" / script), *args, "--json"],
                            capture_output=True, text=True, cwd=str(ROOT))
    if result.returncode != 0:
        raise SystemExit("%s failed: %s" % (script, result.stdout + result.stderr))
    return json.loads(result.stdout)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Batch hiring maths, offline.")
    parser.add_argument("--hires", type=int, default=5)
    parser.add_argument("--base-pay", type=float, default=48000)
    parser.add_argument("--weeks", type=int, default=8)
    args = parser.parse_args(argv)

    funnel = run_json("funnel_calculator.py", "--hires", str(args.hires), "--weeks", str(args.weeks))
    budget = run_json("budget_planner.py", "--base-pay", str(args.base_pay), "--hires", str(args.hires))
    plan = funnel["plan"]

    print("BATCH HIRING: %d people for the same role (starting assumptions, not benchmarks)" % args.hires)
    print()
    print("Make %d offers to land %d hires, because some people say no (%d extra offers)."
          % (plan["offers"], plan["hires"], plan["overhire_offers"]))
    print("Keep a warm backup list of %d finalists you would still like to hire." % plan["backup_list"])
    print()
    print("Funnel, working backwards:")
    for label, key in (("Finalists", "finalists"), ("Interviews", "interviews"), ("Shortlisted", "shortlisted"),
                       ("Screened", "screened"), ("Applicants needed", "applicants"),
                       ("Prospects to contact if you source", "prospects_to_contact")):
        print("  %-38s %d" % (label, plan[key]))
    print()
    print("Time: about %s weeks from first applicant to start." % funnel["timeline"]["lag_weeks"])
    print()
    print("Cost to FIND and HIRE %d people (not salary), by path:" % args.hires)
    for name, path in budget["paths"].items():
        print("  %-20s %10.0f   %s" % (name, path["total_for_all_hires"], path["what"]))
    print()
    print("Rates used (replace with your own):")
    for key, value in funnel["assumptions"].items():
        print("  %-26s %s" % (key, value))
    return 0


if __name__ == "__main__":
    sys.exit(main())
