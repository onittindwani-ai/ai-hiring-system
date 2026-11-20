"""Pipeline tracker: who is at which stage, what is stuck, and what to do next.

Usage:
    python3 tools/pipeline.py init <role>
    python3 tools/pipeline.py add --role <role> --name "Name" [--id C001] [--stage applied]
        [--source form] [--score 72] [--next-action "text"] [--due 2026-12-01] [--notes "text"]
    python3 tools/pipeline.py move --role <role> <candidate_id> <stage> [--confirmed] [--force] [--date YYYY-MM-DD]
    python3 tools/pipeline.py stats --role <role> [--stale-days 7] [--today YYYY-MM-DD]
    python3 tools/pipeline.py weekly --role <role> [--out hiring/<role>/WEEKLY.md]
    (every command also accepts --base DIR, default "hiring", or --file PATH to a pipeline.csv)

What it does:
    Keeps hiring/<role>/pipeline.csv. It checks that stages are real stages, stamps the date of
    every move, shows counts, conversion between consecutive stages, median days in stage and
    stale candidates, and writes a plain weekly report with one next action per stuck person.
    A rejection is a human decision: moving someone to "rejected" needs --confirmed, which you
    pass only after the owner said yes. It only reads and writes local files and never contacts anyone.
    Limit: the CSV holds the current stage only. When someone leaves (rejected, withdrawn) the tool
    stores "last_active:<stage>" in the notes so the funnel maths can still count how far they got.
"""
import argparse
import datetime as dt
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hlib import PIPELINE_COLUMNS, STAGES, TERMINAL_STAGES, read_csv, today_iso, write_csv  # noqa: E402

STAGE_INDEX = {name: index for index, name in enumerate(STAGES)}
MAIN_PATH = STAGES[: STAGE_INDEX["hired"] + 1]
LAST_ACTIVE_RE = re.compile(r"last_active:([a-z_]+)")
LEAVING_STAGES = ("rejected", "withdrawn", "declined")

STAGE_NEXT_ACTION = {
    "sourced": "Send the first message (draft it, then wait for the owner's yes before sending).",
    "applied": "Screen against the scorecard and record a tier.",
    "screened": "Owner decides: shortlist or not shortlisted now.",
    "shortlisted": "Draft the outreach or invitation, send after the owner's yes.",
    "contacted": "Send one polite follow up, or mark no reply and move on.",
    "replied": "Offer two interview times and book one.",
    "interview_scheduled": "Confirm the time and send the interview guide to the interviewer.",
    "interviewed": "Fill the rating sheet and decide the next step.",
    "work_sample": "Score the work sample with its rubric and give feedback.",
    "reference_check": "Make the reference calls with the same questions each time.",
    "offer": "Ask the candidate what is still open and answer it.",
    "accepted": "Confirm the start date and send the onboarding plan.",
}

LOW_CONVERSION_ADVICE = {
    "applied": "Few people reach the applied stage. Check where the post is seen, the pay line and the title, and widen sourcing.",
    "screened": "Many applicants fail the first screen. The post may attract the wrong people, or a must criterion is stricter than the job needs. Re read the must items.",
    "shortlisted": "Screened people rarely make the shortlist. Compare your bar with the maybe tier and check that at least one criterion is not unreachable.",
    "contacted": "Shortlisted people are not being contacted. This is a speed problem on your side: set a day each week for outreach.",
    "replied": "Few contacted people reply. Look at the first message: is it short, specific and honest, and does it say what the job pays?",
    "interview_scheduled": "Replies are not turning into booked interviews. Offer two concrete times and make booking one tap.",
    "interviewed": "Booked interviews are not happening. Check no shows and reschedules, and send a reminder the day before.",
    "work_sample": "Few interviewed people go on to the work sample. Check that the sample is short and clearly paid or time boxed.",
    "reference_check": "Few people reach reference checks. Look at what the interview stage is screening out.",
    "offer": "Few finalists get an offer. Check that your must criteria match what the role really needs.",
    "accepted": "Offers are declined. Ask each person why, and compare pay, start date and speed of your process.",
    "hired": "Accepted offers are not turning into starts. Stay in touch between accept and start date.",
}


def role_file(args):
    if getattr(args, "file", None):
        return Path(args.file)
    if not getattr(args, "role", None):
        raise SystemExit("Tell me which role: add --role <role> (or --file path/to/pipeline.csv).")
    return Path(args.base) / args.role / "pipeline.csv"


def parse_date(text):
    try:
        return dt.date.fromisoformat(str(text).strip())
    except ValueError:
        return None


def effective_stage(row):
    """The furthest stage a person reached, using last_active for people who left."""
    stage = row.get("stage", "")
    if stage == "declined":
        return "offer"
    if stage in ("rejected", "withdrawn"):
        found = LAST_ACTIVE_RE.search(row.get("notes") or "")
        if found and found.group(1) in STAGE_INDEX:
            return found.group(1)
        return "applied"
    return stage


def reached_counts(rows):
    """For each stage on the main path, how many people got there or further."""
    indexes = [STAGE_INDEX.get(effective_stage(r), 0) for r in rows]
    return {name: sum(1 for i in indexes if i >= STAGE_INDEX[name]) for name in MAIN_PATH}


def conversions(rows):
    reached = reached_counts(rows)
    result = []
    for before, after in zip(MAIN_PATH, MAIN_PATH[1:]):
        n_from, n_to = reached[before], reached[after]
        result.append({"from": before, "to": after, "n_from": n_from, "n_to": n_to,
                       "rate": (n_to / n_from) if n_from else None})
    return result


def stale_rows(rows, today, stale_days=7):
    found = []
    for row in rows:
        if row.get("stage") in TERMINAL_STAGES:
            continue
        changed = parse_date(row.get("stage_changed_on", ""))
        if changed and (today - changed).days > stale_days:
            found.append((row, (today - changed).days))
    return sorted(found, key=lambda item: -item[1])


def median_days_by_stage(rows, today):
    buckets = {}
    for row in rows:
        changed = parse_date(row.get("stage_changed_on", ""))
        if changed and row.get("stage") not in TERMINAL_STAGES:
            buckets.setdefault(row["stage"], []).append((today - changed).days)
    return {stage: statistics.median(days) for stage, days in buckets.items()}


def next_id(rows):
    numbers = [int(m.group(1)) for r in rows for m in [re.fullmatch(r"C(\d+)", r.get("candidate_id", ""))] if m]
    return "C%03d" % (max(numbers, default=0) + 1)


def with_last_active(notes, stage):
    cleaned = LAST_ACTIVE_RE.sub("", notes or "").strip()
    token = "last_active:%s" % stage
    return (cleaned + " " + token).strip()


def apply_move(rows, candidate_id, stage, when, confirmed=False, force=False):
    """Return (new_rows, problem). problem is None when the move is allowed."""
    if stage not in STAGE_INDEX:
        return rows, "Unknown stage '%s'. Stages: %s." % (stage, ", ".join(STAGES))
    match = [r for r in rows if r.get("candidate_id") == candidate_id]
    if not match:
        return rows, "No candidate with id %s in this pipeline." % candidate_id
    current = match[0]["stage"]
    if stage == "rejected" and not confirmed:
        return rows, ("A rejection is a human decision. Re run with --confirmed once the owner has said yes "
                      "to rejecting %s." % candidate_id)
    if current in TERMINAL_STAGES and not force:
        allowed = {"accepted": ("hired", "withdrawn", "declined")}.get(current, ())
        if stage not in allowed:
            return rows, "%s is already %s (closed). Use --force only to correct a mistake." % (candidate_id, current)
    elif (stage not in TERMINAL_STAGES and STAGE_INDEX[stage] < STAGE_INDEX.get(current, 0)
          and not force):
        return rows, "That moves %s backwards (%s to %s). Use --force if it is a correction." % (candidate_id, current, stage)
    updated = []
    for row in rows:
        if row.get("candidate_id") == candidate_id:
            row = dict(row, stage=stage, stage_changed_on=when)
            if stage in LEAVING_STAGES:
                row["notes"] = with_last_active(row.get("notes"), current)
        updated.append(row)
    return updated, None


def build_stats_text(rows, today, stale_days):
    lines = ["Candidates: %d" % len(rows), "", "Where people are now:"]
    for stage in STAGES:
        count = sum(1 for r in rows if r.get("stage") == stage)
        if count:
            lines.append("  %-20s %d" % (stage, count))
    lines += ["", "Conversion between consecutive stages (people who got that far, including those who moved on):"]
    for item in conversions(rows):
        if item["n_from"] == 0:
            continue
        lines.append("  %-20s to %-20s %d of %d (%.0f%%)" % (
            item["from"], item["to"], item["n_to"], item["n_from"], 100 * item["rate"]))
    medians = median_days_by_stage(rows, today)
    lines += ["", "Median days in the current stage:"]
    lines += ["  %-20s %s" % (s, ("%g" % medians[s])) for s in STAGES if s in medians] or ["  (no dated rows yet)"]
    stale = stale_rows(rows, today, stale_days)
    lines += ["", "Stale (more than %d days in the same stage): %d" % (stale_days, len(stale))]
    lines += ["  %s %s, %s, %d days" % (r["candidate_id"], r.get("name", ""), r["stage"], days) for r, days in stale]
    return "\n".join(lines)


def build_weekly(rows, today, stale_days=7):
    lines = ["# Weekly hiring report", "", "Date: %s" % today.isoformat(), "",
             "## Where everyone is", ""]
    for stage in STAGES:
        count = sum(1 for r in rows if r.get("stage") == stage)
        if count:
            lines.append("- %s: %d" % (stage, count))
    if not rows:
        lines.append("- No candidates yet.")
    lines += ["", "## Conversion in your own data", ""]
    usable = [c for c in conversions(rows) if c["n_from"] >= 5]
    for item in conversions(rows):
        if item["n_from"]:
            lines.append("- %s to %s: %d of %d (%.0f%%)" % (item["from"], item["to"], item["n_to"],
                                                           item["n_from"], 100 * item["rate"]))
    if usable:
        weakest = min(usable, key=lambda c: c["rate"])
        lines += ["", "Lowest step with at least 5 people behind it: %s to %s (%.0f%%)." % (
            weakest["from"], weakest["to"], 100 * weakest["rate"]),
            "What to change: " + LOW_CONVERSION_ADVICE.get(weakest["to"], "Look at what happens between these two stages.")]
    else:
        lines += ["", "Not enough data yet to judge a weak step (a step needs at least 5 people before it)."]
    stale = stale_rows(rows, today, stale_days)
    lines += ["", "## Stuck for more than %d days" % stale_days, ""]
    if not stale:
        lines.append("- Nobody is stuck. Good.")
    for row, days in stale:
        logged = (row.get("next_action") or "").strip()
        action = ("%s (due %s)" % (logged, row.get("next_action_due") or "no date")
                  if logged else STAGE_NEXT_ACTION.get(row["stage"], "Decide the next step."))
        lines.append("- %s %s, %s for %d days. Next action: %s" % (
            row["candidate_id"], row.get("name", ""), row["stage"], days, action))
    lines += ["", "Nothing is sent, posted or rejected without the owner's yes."]
    return "\n".join(lines) + "\n"


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--role")
    common.add_argument("--base", default="hiring")
    common.add_argument("--file")
    parser = argparse.ArgumentParser(description="Hiring pipeline tracker")
    sub = parser.add_subparsers(dest="command", required=True)
    p_init = sub.add_parser("init", parents=[common])
    p_init.add_argument("init_role", nargs="?")
    p_add = sub.add_parser("add", parents=[common])
    for name in ("name", "id", "source", "score", "next_action", "due", "notes"):
        p_add.add_argument("--" + name.replace("_", "-"), dest=name, default="")
    p_add.add_argument("--stage", default="applied")
    p_move = sub.add_parser("move", parents=[common])
    p_move.add_argument("candidate_id")
    p_move.add_argument("stage")
    p_move.add_argument("--confirmed", action="store_true")
    p_move.add_argument("--force", action="store_true")
    p_move.add_argument("--date")
    p_stats = sub.add_parser("stats", parents=[common])
    p_week = sub.add_parser("weekly", parents=[common])
    p_week.add_argument("--out")
    for p in (p_stats, p_week):
        p.add_argument("--stale-days", type=int, default=7)
        p.add_argument("--today")
    return parser


def resolve_today(text):
    if not text:
        return dt.date.today()
    parsed = parse_date(text)
    if parsed is None:
        raise SystemExit("--today must look like 2026-12-01.")
    return parsed


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "init" and args.init_role:
        args.role = args.init_role
    try:
        path = role_file(args)
    except SystemExit as exc:
        print(exc)
        return 1
    if args.command == "init":
        if path.exists():
            print("Already there: %s (left as it is)." % path)
            return 0
        write_csv(path, PIPELINE_COLUMNS, [])
        print("Created %s" % path)
        return 0
    if not path.exists():
        print("No pipeline file at %s. Run: python3 tools/pipeline.py init <role>" % path)
        return 1
    rows = read_csv(path)
    if args.command == "add":
        return cmd_add(args, path, rows)
    if args.command == "move":
        when = args.date or today_iso()
        if parse_date(when) is None:
            print("--date must look like 2026-12-01.")
            return 1
        new_rows, problem = apply_move(rows, args.candidate_id, args.stage, when, args.confirmed, args.force)
        if problem:
            print(problem)
            return 1
        write_csv(path, PIPELINE_COLUMNS, new_rows)
        print("%s is now %s (%s)." % (args.candidate_id, args.stage, when))
        return 0
    today = resolve_today(args.today)
    if args.command == "stats":
        print(build_stats_text(rows, today, args.stale_days))
        return 0
    out = Path(args.out) if args.out else path.parent / "WEEKLY.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_weekly(rows, today, args.stale_days), encoding="utf-8")
    print("Wrote %s" % out)
    return 0


def cmd_add(args, path, rows):
    if args.stage not in STAGE_INDEX:
        print("Unknown stage '%s'. Stages: %s." % (args.stage, ", ".join(STAGES)))
        return 1
    if not args.name:
        print("Give the person a name with --name.")
        return 1
    candidate_id = args.id or next_id(rows)
    if any(r.get("candidate_id") == candidate_id for r in rows):
        print("The id %s is already in the pipeline." % candidate_id)
        return 1
    row = {"candidate_id": candidate_id, "name": args.name, "stage": args.stage, "stage_changed_on": today_iso(),
           "source": args.source, "score": args.score, "next_action": args.next_action,
           "next_action_due": args.due, "notes": args.notes}
    write_csv(path, PIPELINE_COLUMNS, rows + [row])
    print("Added %s (%s) at stage %s." % (candidate_id, args.name, args.stage))
    return 0


if __name__ == "__main__":
    sys.exit(main())
