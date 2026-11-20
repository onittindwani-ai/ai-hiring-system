"""New role scaffold: creates the work folder for one hire.

Usage:
    python3 tools/new_role.py bookkeeper
    python3 tools/new_role.py sales-development-rep --scorecard templates/scorecards/sales-development-rep.json
    python3 tools/new_role.py bookkeeper --base hiring

What it does:
    Creates hiring/<role-slug>/ with inbox/ (exports and pasted lists go here), candidates/,
    drafts/ (every message and post waits here for the owner's yes), scorecard.json (a copy of the
    scorecard you pass, or an empty skeleton), prospects.csv and pipeline.csv with their headers,
    and plan.md with the questions to settle first. It refuses to touch a role folder that already
    exists. The hiring/ folder is ignored by git, so real candidate data stays on your computer.
"""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hlib import PIPELINE_COLUMNS, PROSPECT_COLUMNS, load_json, save_json, slug, today_iso, write_csv  # noqa: E402

PLAN_STUB = """# Hiring plan: {title}

Created: {date}. Status: draft. Nothing is posted or sent until the owner says yes.

## 1. Why this hire now

- What problem does it solve, and how will we know in 90 days?

## 2. Hire or automate

- Which parts of the job could AI or a tool do? (see docs/knowledge/04-HIRE-OR-AUTOMATE.md)

## 3. How many people and how fast

- Run: python3 tools/funnel_calculator.py --hires N
- Target start date:

## 4. Budget

- Run: python3 tools/budget_planner.py --base-pay X --hires N --budget Y
- Pay range (checked against a source, with the date):

## 5. Sourcing

- Run: python3 tools/make_search_strings.py hiring/{slug}/scorecard.json --location "City"
- Put exports and pasted lists in inbox/. Drafts go in drafts/.

## 6. Decisions needed from the owner

- [ ] Scorecard approved
- [ ] Job post approved
- [ ] First outreach messages approved
"""


def skeleton_scorecard(role_slug):
    return {"version": 1, "role_id": role_slug, "title": role_slug.replace("-", " ").title(), "level": "",
            "mission": "", "outcomes_90_days": [], "criteria": [], "gates": [], "deal_breakers": [],
            "work_sample": {"title": "", "brief": "", "time_limit_minutes": 45, "how_to_score": ""},
            "interview_questions": [], "red_flags": [], "sourcing_channels": [],
            "pay_research_hint": "", "automation_note": ""}


def scaffold(role, base="hiring", scorecard=None):
    """Create the folder. Returns the role folder path. Raises FileExistsError / FileNotFoundError / ValueError."""
    role_slug = slug(role)
    if not role_slug:
        raise ValueError("Give the role a name with letters or numbers, for example: bookkeeper")
    folder = Path(base) / role_slug
    if folder.exists():
        raise FileExistsError("hiring/%s already exists. I did not touch it." % role_slug)
    if scorecard and not Path(scorecard).is_file():
        raise FileNotFoundError("Scorecard not found: %s" % scorecard)
    for name in ("inbox", "candidates", "drafts"):
        (folder / name).mkdir(parents=True)
        (folder / name / ".gitkeep").write_text("", encoding="utf-8")
    if scorecard:
        shutil.copyfile(scorecard, folder / "scorecard.json")
        title = load_json(folder / "scorecard.json").get("title", role_slug)
    else:
        save_json(folder / "scorecard.json", skeleton_scorecard(role_slug))
        title = role_slug.replace("-", " ").title()
    write_csv(folder / "prospects.csv", PROSPECT_COLUMNS, [])
    write_csv(folder / "pipeline.csv", PIPELINE_COLUMNS, [])
    (folder / "plan.md").write_text(PLAN_STUB.format(title=title, date=today_iso(), slug=role_slug), encoding="utf-8")
    return folder


def main(argv=None):
    parser = argparse.ArgumentParser(description="Create the work folder for a new role")
    parser.add_argument("role")
    parser.add_argument("--scorecard")
    parser.add_argument("--base", default="hiring")
    args = parser.parse_args(argv)
    try:
        folder = scaffold(args.role, args.base, args.scorecard)
    except (FileExistsError, FileNotFoundError, ValueError) as exc:
        print(exc)
        return 1
    print("Created %s with inbox/, candidates/, drafts/, scorecard.json, prospects.csv, pipeline.csv, plan.md" % folder)
    print("Next: open plan.md, then ask Claude to write or check the scorecard.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
