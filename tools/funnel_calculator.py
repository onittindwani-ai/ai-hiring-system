"""Funnel calculator: how many people you need at each stage to make N hires.

Usage:
    python3 tools/funnel_calculator.py --hires 3
    python3 tools/funnel_calculator.py --hires 5 --weeks 8
    python3 tools/funnel_calculator.py --hires 2 --weekly-applicants 12
    python3 tools/funnel_calculator.py --hires 3 --assumptions my_rates.json
    python3 tools/funnel_calculator.py --hires 3 --actual hiring/<role>/pipeline.csv
    python3 tools/funnel_calculator.py --hires 3 --json

What it does:
    Works backwards from the number of hires to offers, finalists, interviews, shortlisted people,
    screened people, applicants and prospects to contact. For several identical hires it also
    plans extra offers (people say no) and a warm backup list. The conversion rates are STARTING
    ASSUMPTIONS for planning, printed every time. They are not benchmarks. Replace them with your
    own numbers in a JSON file, or pass --actual with your pipeline.csv: any step with at least
    5 people behind it then uses your real observed rate instead of the assumption.
"""
import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hlib import read_csv  # noqa: E402
from pipeline import STAGE_INDEX, effective_stage  # noqa: E402

# STARTING ASSUMPTIONS: planning numbers only, replace with your own data.
STARTING_ASSUMPTIONS = {
    "offer_acceptance": 0.80,
    "finalist_to_offer": 0.50,
    "interview_to_finalist": 0.40,
    "shortlist_to_interview": 0.70,
    "screened_to_shortlist": 0.50,
    "applicant_to_screened": 0.60,
    "prospect_to_applicant": 0.10,
    "backup_share_of_hires": 0.50,
    "weeks_applied_to_offer": 4,
    "weeks_offer_to_start": 2,
}

RATE_KEYS = [k for k in STARTING_ASSUMPTIONS if k not in ("backup_share_of_hires", "weeks_applied_to_offer", "weeks_offer_to_start")]

# Which pipeline stages bound each observed step: key -> (from_stage, to_stage)
OBSERVED_STEPS = {
    "applicant_to_screened": ("applied", "screened"),
    "screened_to_shortlist": ("screened", "shortlisted"),
    "shortlist_to_interview": ("shortlisted", "interview_scheduled"),
    "interview_to_finalist": ("interviewed", "work_sample"),
    "finalist_to_offer": ("work_sample", "offer"),
    "offer_acceptance": ("offer", "accepted"),
}
MIN_PEOPLE = 5


def observed_rates(pipeline_rows):
    """Real conversion rates from a pipeline, only where at least 5 people reached the step's start."""
    indexes = [STAGE_INDEX.get(effective_stage(r), 0) for r in pipeline_rows]
    found = {}
    for key, (start, end) in OBSERVED_STEPS.items():
        n_start = sum(1 for i in indexes if i >= STAGE_INDEX[start])
        n_end = sum(1 for i in indexes if i >= STAGE_INDEX[end])
        if n_start >= MIN_PEOPLE and n_end > 0:
            found[key] = {"rate": n_end / n_start, "from": n_start, "to": n_end}
    return found


def merge_assumptions(base, overrides):
    unknown = [k for k in overrides if k not in base]
    if unknown:
        raise ValueError("Unknown assumption(s): %s. Known: %s." % (", ".join(unknown), ", ".join(base)))
    merged = dict(base)
    merged.update({k: float(v) for k, v in overrides.items()})
    for key in RATE_KEYS:
        if not 0 < merged[key] <= 1:
            raise ValueError("%s must be above 0 and at most 1 (you gave %s)." % (key, merged[key]))
    if merged["backup_share_of_hires"] < 0:
        raise ValueError("backup_share_of_hires cannot be negative.")
    return merged


def up(value):
    """Round up to a whole number, ignoring float noise like 3.0000000000000004."""
    return math.ceil(round(value, 9))


def plan(hires, rates):
    """Work backwards from hires. Returns a dict of whole numbers (rounded up)."""
    offers = up(hires / rates["offer_acceptance"])
    finalists = up(offers / rates["finalist_to_offer"])
    interviews = up(finalists / rates["interview_to_finalist"])
    shortlisted = up(interviews / rates["shortlist_to_interview"])
    screened = up(shortlisted / rates["screened_to_shortlist"])
    applicants = up(screened / rates["applicant_to_screened"])
    prospects = up(applicants / rates["prospect_to_applicant"])
    return {
        "hires": hires, "offers": offers, "overhire_offers": offers - hires,
        "finalists": finalists, "interviews": interviews, "shortlisted": shortlisted,
        "screened": screened, "applicants": applicants, "prospects_to_contact": prospects,
        "backup_list": max(1, up(hires * rates["backup_share_of_hires"])),
    }


def timeline(result, rates, weeks, weekly_applicants):
    lag = rates["weeks_applied_to_offer"] + rates["weeks_offer_to_start"]
    out = {"lag_weeks": lag}
    if weeks:
        out["applicants_needed_per_week"] = up(result["applicants"] / weeks)
        out["target_weeks"] = weeks
    if weekly_applicants:
        collect = up(result["applicants"] / weekly_applicants)
        out["weekly_applicants"] = weekly_applicants
        out["weeks_to_collect_applicants"] = collect
        out["weeks_to_fill"] = collect + lag
    return out


def build_report(hires, rates, sources, weeks=None, weekly_applicants=None):
    result = plan(hires, rates)
    return {"assumptions": rates, "assumption_sources": sources, "plan": result,
            "timeline": timeline(result, rates, weeks, weekly_applicants),
            "note": "Starting assumptions are planning numbers, not benchmarks. Replace them with your own data."}


def format_report(report):
    plan_ = report["plan"]
    lines = ["FUNNEL PLAN FOR %d HIRE%s" % (plan_["hires"], "" if plan_["hires"] == 1 else "S"), ""]
    rows = [("Hires wanted", plan_["hires"]), ("Offers to make", plan_["offers"]),
            ("Finalists (work sample, references)", plan_["finalists"]),
            ("Interviews to run", plan_["interviews"]), ("People to shortlist", plan_["shortlisted"]),
            ("People to screen", plan_["screened"]), ("Applicants needed", plan_["applicants"]),
            ("Prospects to contact (only if you source, not if people apply by themselves)",
             plan_["prospects_to_contact"])]
    lines += ["  %-72s %d" % row for row in rows]
    if plan_["hires"] > 1:
        lines += ["", "Batch hiring: %d extra offer(s) are planned because some people will say no." % plan_["overhire_offers"]]
    lines += ["Keep a warm backup list of %d finalist(s) you would still like to hire." % plan_["backup_list"], ""]
    lines.append("STARTING ASSUMPTIONS (planning numbers only, replace with your own data):")
    for key, value in report["assumptions"].items():
        source = report["assumption_sources"].get(key, "starting assumption")
        lines.append("  %-26s %-6g %s" % (key, value, source))
    time_ = report["timeline"]
    lines += ["", "Time:", "  Assumed lag: %g weeks (first applicant to offer plus offer to start)" % time_["lag_weeks"]]
    if "applicants_needed_per_week" in time_:
        lines.append("  To fill in %d weeks you need about %d applicants per week." % (
            time_["target_weeks"], time_["applicants_needed_per_week"]))
    if "weeks_to_fill" in time_:
        lines.append("  At %d applicants per week: about %d weeks to collect them, about %d weeks to fill." % (
            time_["weekly_applicants"], time_["weeks_to_collect_applicants"], time_["weeks_to_fill"]))
    lines += ["", report["note"]]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Work backwards from hires to the people you need at each stage")
    parser.add_argument("--hires", type=int, required=True)
    parser.add_argument("--assumptions", help="JSON file that overrides some starting assumptions")
    parser.add_argument("--actual", help="a pipeline.csv: use your real rates where at least 5 people reached a step")
    parser.add_argument("--weeks", type=float, help="target weeks to fill")
    parser.add_argument("--weekly-applicants", type=float, dest="weekly_applicants")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.hires < 1:
        print("--hires must be 1 or more.")
        return 1
    sources = {k: "starting assumption" for k in STARTING_ASSUMPTIONS}
    overrides = {}
    try:
        if args.assumptions:
            overrides = json.loads(Path(args.assumptions).read_text(encoding="utf-8"))
            sources.update({k: "from %s" % Path(args.assumptions).name for k in overrides})
        rates = merge_assumptions(STARTING_ASSUMPTIONS, overrides)
        if args.actual:
            actual = observed_rates(read_csv(args.actual))
            rates = merge_assumptions(rates, {k: v["rate"] for k, v in actual.items()})
            sources.update({k: "observed: %d of %d people" % (v["to"], v["from"]) for k, v in actual.items()})
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("Problem: %s" % exc)
        return 1
    report = build_report(args.hires, rates, sources, args.weeks, args.weekly_applicants)
    print(json.dumps(report, indent=2) if args.json else format_report(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
