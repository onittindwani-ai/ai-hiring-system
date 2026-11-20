"""Interview kit: an interview guide and a rating sheet built from a scorecard.

Usage:
    python3 tools/interview_kit.py templates/scorecards/bookkeeper.json
    python3 tools/interview_kit.py <scorecard.json> --out hiring/<role>/interviews
    python3 tools/interview_kit.py <scorecard.json> --out hiring/<role>/interviews --candidate C001 --interviewer "Sam"

What it does:
    Writes two files into the output folder (default: interview-kit): interview-guide.md, with the
    same questions in the same order for every candidate, what good and weak answers look like,
    the 0 to 4 anchors for each criterion, the work sample and what never to ask; and
    rating-sheet.csv, one row per criterion, to fill in during or right after the interview.
    The final score is the sum of weight times level divided by 4. A person decides every outcome.
"""
import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hlib import load_json  # noqa: E402

SHEET_COLUMNS = ["candidate_id", "interviewer", "criterion_id", "criterion_name", "type", "weight",
                 "min_level", "level_0_to_4", "evidence_notes"]

NEVER_ASK = [
    "Age, birth year, or how long until retirement.",
    "Gender, pregnancy, plans for children, marital or family status.",
    "Religion, race, ethnicity, nationality or where someone was 'really' from.",
    "Health, disability or medication (ask only whether they can do the listed duties, with or without adjustments).",
    "Photos, names or accents as a reason for anything.",
    "Anything not tied to the job. If you would not ask every candidate, do not ask.",
]


def questions_for(scorecard, criterion):
    asked = [q for q in scorecard.get("interview_questions", []) if q.get("criterion_id") == criterion["id"]]
    if asked:
        return asked
    return [{"criterion_id": criterion["id"],
             "question": "Walk me through a real example from your own work that shows this: %s"
                         % criterion.get("what_good_looks_like", criterion["name"]),
             "good_answer_signs": criterion.get("evidence_needed", []), "weak_answer_signs": []}]


def build_guide(scorecard):
    lines = ["# Interview guide: %s" % scorecard["title"], "",
             "Purpose of the role: %s" % scorecard.get("mission", ""), "",
             "## How to run it", "",
             "- Ask every candidate the same questions in the same order. Take notes on what they said, not on how you felt.",
             "- Score each criterion from 0 to 4 using the anchors below, right after the interview, before you talk to anyone else.",
             "- Write one piece of evidence for every score.",
             "- Final score = sum of (weight x level / 4). It informs the decision. A person decides.", "",
             "## Questions by criterion", ""]
    for criterion in scorecard["criteria"]:
        lines += ["### %s (%s, weight %s, minimum level %s)" % (
            criterion["name"], criterion.get("type", "nice"), criterion["weight"], criterion.get("min_level", "none")), ""]
        for q in questions_for(scorecard, criterion):
            lines += ["**Question:** %s" % q["question"], ""]
            if q.get("good_answer_signs"):
                lines += ["Good answer signs:"] + ["- " + s for s in q["good_answer_signs"]] + [""]
            if q.get("weak_answer_signs"):
                lines += ["Weak answer signs:"] + ["- " + s for s in q["weak_answer_signs"]] + [""]
        lines += ["Scoring anchors:"] + ["- " + level for level in criterion.get("levels", [])] + [""]
    sample = scorecard.get("work_sample") or {}
    if sample.get("title"):
        lines += ["## Work sample", "", "**%s** (%s minutes)" % (sample["title"], sample.get("time_limit_minutes", "?")), "",
                  sample.get("brief", ""), "", "How to score: %s" % sample.get("how_to_score", ""), ""]
    if scorecard.get("gates"):
        lines += ["## Gates (ask the same way for everyone)", ""] + [
            "- %s (%s)" % (g["question"], g.get("kind", "hard")) for g in scorecard["gates"]] + [""]
    if scorecard.get("red_flags"):
        lines += ["## Red flags to note, not to judge on their own", ""] + ["- " + r for r in scorecard["red_flags"]] + [""]
    lines += ["## Never ask", ""] + ["- " + n for n in NEVER_ASK]
    lines += ["", "This guide is general information, not legal advice."]
    return "\n".join(lines) + "\n"


def sheet_rows(scorecard, candidate_id="", interviewer=""):
    return [{"candidate_id": candidate_id, "interviewer": interviewer, "criterion_id": c["id"],
             "criterion_name": c["name"], "type": c.get("type", ""), "weight": c["weight"],
             "min_level": c.get("min_level", ""), "level_0_to_4": "", "evidence_notes": ""}
            for c in scorecard["criteria"]]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build an interview guide and rating sheet from a scorecard")
    parser.add_argument("scorecard")
    parser.add_argument("--out", default="interview-kit")
    parser.add_argument("--candidate", default="")
    parser.add_argument("--interviewer", default="")
    args = parser.parse_args(argv)
    path = Path(args.scorecard)
    if not path.exists():
        print("Scorecard not found: %s" % path)
        return 1
    try:
        scorecard = load_json(path)
        guide = build_guide(scorecard)
        rows = sheet_rows(scorecard, args.candidate, args.interviewer)
    except (ValueError, KeyError, TypeError) as exc:
        print("This does not look like a valid scorecard (%s). Run tools/validate_scorecard.py first." % exc)
        return 1
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "interview-guide.md").write_text(guide, encoding="utf-8")
    with open(out / "rating-sheet.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SHEET_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print("Wrote %s and %s" % (out / "interview-guide.md", out / "rating-sheet.csv"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
