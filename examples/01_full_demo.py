"""Example 1: the whole hiring funnel on the made up company, offline, in under 20 seconds.

Usage:
    python3 examples/01_full_demo.py

What it does:
    Takes the fictional Northlight Home Services and its Sales Development Rep role and runs every
    step the real system runs, with the real tools, on fake data:
      1. creates a role folder in a temporary place (tools/new_role.py)
      2. plans the money and the numbers (tools/budget_planner.py, tools/funnel_calculator.py)
      3. checks the scorecard (tools/validate_scorecard.py)
      4. builds search strings (tools/make_search_strings.py), shown but never run
      5. scores the 20 made up SDR candidates blind, with the offline rules engine and with the
         FAKE mock Jev (a practice server started on your own computer), then measures both against
         the hand written answer key (tools/score_candidates.py, tools/evaluate.py)
      6. shows the shortlist and who needs a person to look first
      7. renders two message drafts (tools/render_message.py)
    Nothing is sent, posted or saved outside the temporary folder. No network, no key.
    The sample resumes never state work authorization, so the demo scores with --unknown-gates flag:
    the gate stays flagged for a person, but the tier is still shown.
    The scores come from baselines, not from the real Jev or from Claude: use them to see how the
    flow works, never to judge a real person.
"""
import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
SAMPLE = ROOT / "data" / "sample"
ROLE = "sales-development-rep"

MESSAGE_VALUES = {
    "candidate_first_name": "Alex", "role_title": "Sales Development Rep", "company_name": "Northlight Home Services",
    "recruiter_name": "Jordan Example", "booking_link": "https://example.com/book", "pay_range": "$40,000 to $48,000 a year",
    "start_date": "early January", "call_length": "20 minutes", "first_outcome": "book 10 qualified estimates a week",
    "specific_detail": "Your example outreach notes were clear and short",
}


def run(script, *args, check=True):
    result = subprocess.run([sys.executable, str(TOOLS / script), *args], capture_output=True, text=True, cwd=str(ROOT))
    if check and result.returncode != 0:
        raise SystemExit("%s failed:\n%s" % (script, result.stdout + result.stderr))
    return result.stdout.strip()


def heading(text):
    print("\n=== %s ===" % text)


def lines_matching(text, *starts):
    return [line for line in text.splitlines() if line.strip().startswith(starts)]


def read_role_candidates():
    rows = []
    for line in (SAMPLE / "candidates.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            item = json.loads(line)
            if item.get("role_id") == ROLE:
                rows.append(item)
    return rows


def main():
    print("AI Hiring System, full offline demo. Everything below is made up. Nothing is sent.")
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "hiring"
        card = str(SAMPLE / ("scorecard-%s.json" % ROLE))

        heading("1. New role folder")
        print(run("new_role.py", ROLE, "--base", str(base), "--scorecard", card).splitlines()[0].replace(tmp, "<temp>"))
        role_dir = base / ROLE

        heading("2. Plan the money and the numbers (starting assumptions, replace with your own)")
        budget = run("budget_planner.py", "--base-pay", "44000", "--hires", "1", "--budget", "1500")
        print("\n".join(lines_matching(budget, "Fully loaded", "Budget tier", "Recommendation", "Cheapest way"))[:900])
        funnel = json.loads(run("funnel_calculator.py", "--hires", "1", "--json"))["plan"]
        print("For 1 hire plan on %(offers)d offer, %(finalists)d finalists, %(interviews)d interviews, "
              "%(shortlisted)d shortlisted, %(screened)d screened, %(applicants)d applicants." % funnel)

        heading("3. Check the scorecard")
        verdict = run("validate_scorecard.py", card).replace(str(ROOT) + "/", "")
        print("\n".join(verdict.splitlines()[-2:]))

        heading("4. Search strings (Claude may run only the Google ones, you run the rest in your own accounts)")
        strings = run("make_search_strings.py", card, "--location", "Leeds")
        print("\n".join(line for line in strings.splitlines() if line.startswith("## ") or line.startswith("Who runs it")))

        heading("5. Score the 20 made up candidates blind, then measure against the answer key")
        candidates = read_role_candidates()
        cand_path = role_dir / "candidates" / "sample.jsonl"
        cand_path.write_text("\n".join(json.dumps(c) for c in candidates) + "\n", encoding="utf-8")
        key = json.loads((SAMPLE / "answer_key.json").read_text(encoding="utf-8"))
        key["candidates"] = {cid: v for cid, v in key["candidates"].items() if v.get("role_id") == ROLE}
        key_path = Path(tmp) / "answer_key.json"
        key_path.write_text(json.dumps(key), encoding="utf-8")
        for engine in ("rules", "mock"):
            out = role_dir / ("scores-%s.json" % engine)
            shortlist = role_dir / ("shortlist-%s.csv" % engine)
            print("\n-- engine: %s%s" % (engine, " (a FAKE Jev for practice, not the real model)" if engine == "mock" else ""))
            text = run("score_candidates.py", "run", "--scorecard", card, "--candidates", str(cand_path), "--engine", engine,
                       "--unknown-gates", "flag", "--out", str(out), "--shortlist", str(shortlist))
            print("\n".join(line for line in text.splitlines() if not line.startswith("Wrote")))
            report = run("evaluate.py", "--scores", str(out), "--key", str(key_path))
            print("\n".join(lines_matching(report, "Same tier", "Same or", "Dangerous"))[:600])

        print("\nBoth baselines miss people the answer key calls strong. That is why a person looks at everything,")
        print("and why the real Jev or Claude reading the redacted text is the better scorer. See docs/SAMPLE-RESULTS.md.")

        heading("6. Shortlist from the rules engine (a person decides every no and every yes)")
        with open(role_dir / "shortlist-rules.csv", encoding="utf-8", newline="") as handle:
            for row in list(csv.DictReader(handle))[:8]:
                print("  #%-2s %s  %-6s score %-5s needs a person: %-5s %s" % (
                    row["rank"], row["candidate_id"], row["tier"], row["weighted_score"], row["needs_human"], row["flags"]))

        heading("7. Two message drafts (drafts only, nothing is sent)")
        vars_path = Path(tmp) / "vars.json"
        vars_path.write_text(json.dumps(MESSAGE_VALUES), encoding="utf-8")
        for name in ("08-screening-invite.md", "14-decline-after-application.md"):
            out = role_dir / "drafts" / name
            print(run("render_message.py", str(ROOT / "templates" / "messages" / name), "--vars", str(vars_path),
                      "--out", str(out)).replace(tmp, "<temp>"))
        print("\nFirst lines of the screening invite:")
        print("\n".join((role_dir / "drafts" / "08-screening-invite.md").read_text(encoding="utf-8").splitlines()[:12]))

    print("\nSUMMARY: one role set up, numbers planned, scorecard valid, 20 people scored blind two ways,")
    print("both baselines measured against a hand made key, 2 drafts written. Real work needs your own data,")
    print("Claude reading the redacted texts, and your yes before anything is sent. This is not legal advice.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
