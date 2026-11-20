"""Shared helpers for the AI Hiring System tools (Python 3.9+, standard library only).

Usage:
    from hlib import STAGES, load_json, save_json, read_candidates, weighted_score, tier_for

What it does:
    Holds the constants and small functions every tool uses, so the tools agree on stages,
    tiers, score maths and file formats. It never touches the network.
"""
import csv
import datetime as _dt
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STAGES = [
    "sourced", "applied", "screened", "shortlisted", "contacted", "replied",
    "interview_scheduled", "interviewed", "work_sample", "reference_check",
    "offer", "accepted", "hired", "declined", "rejected", "withdrawn",
]
TERMINAL_STAGES = ["accepted", "hired", "declined", "rejected", "withdrawn"]
CONTACT_STATUSES = ["not_contacted", "contacted", "replied", "interested", "not_interested", "stopped"]
PROSPECT_SOURCES = ["google_search", "github", "portfolio", "community", "referral", "board_export", "event", "company_site"]
CANDIDATE_SOURCES = ["form", "email", "board_export", "sourced", "referral"]
TIERS = ["strong", "maybe", "review", "below"]

PROSPECT_COLUMNS = ["prospect_id", "role_id", "name", "headline", "location", "public_url", "source",
                    "found_on", "fit_note", "contact_status", "opt_out", "notes"]
PIPELINE_COLUMNS = ["candidate_id", "name", "stage", "stage_changed_on", "source", "score",
                    "next_action", "next_action_due", "notes"]
SHORTLIST_COLUMNS = ["rank", "candidate_id", "tier", "weighted_score", "needs_human", "top_reasons", "flags"]

STRONG_SCORE = 75.0
MAYBE_SCORE = 55.0
CONFIDENCE_OK = 0.8
CONFIDENCE_LOW = 0.6


def today_iso():
    return _dt.date.today().isoformat()


def slug(text):
    """Lowercase, letters, digits and single hyphens only."""
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", str(text).lower())).strip("-")


def load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, columns, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_candidates(path):
    """Read candidates from .json (list), .jsonl, .csv, or a folder of .txt files (one resume each)."""
    target = Path(path)
    if target.is_dir():
        rows = []
        for index, file in enumerate(sorted(target.glob("*.txt")), start=1):
            rows.append({"candidate_id": "T%03d" % index, "name": file.stem, "source": "board_export",
                         "resume_text": file.read_text(encoding="utf-8"), "answers": {}})
        return rows
    suffix = target.suffix.lower()
    if suffix == ".jsonl":
        with open(target, encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    if suffix == ".json":
        data = load_json(target)
        return data if isinstance(data, list) else data.get("candidates", [])
    if suffix == ".csv":
        return read_csv(target)
    raise ValueError("Unsupported candidate file: %s (use .json, .jsonl, .csv or a folder of .txt)" % path)


def candidate_text(candidate):
    """The text that gets scored: the resume plus any written answers."""
    parts = [str(candidate.get("resume_text", "")).strip()]
    answers = candidate.get("answers") or {}
    for key in sorted(answers):
        parts.append("%s: %s" % (key, answers[key]))
    return "\n\n".join(part for part in parts if part)


def weighted_score(scorecard, levels):
    """Sum of weight * level / 4 over the scorecard criteria. `levels` maps criterion id to 0..4."""
    total = 0.0
    for criterion in scorecard["criteria"]:
        level = max(0, min(4, int(levels.get(criterion["id"], 0))))
        total += criterion["weight"] * level / 4.0
    return round(total, 1)


def must_failures(scorecard, levels):
    """Ids of must criteria whose level is under their min_level."""
    return [c["id"] for c in scorecard["criteria"]
            if c.get("type") == "must" and int(levels.get(c["id"], 0)) < int(c.get("min_level", 1))]


def tier_for(score, must_failed, hard_fail, flagged):
    """Tier rule from BUILD-SPEC: review (flags) beats everything, then strong, maybe, below."""
    if flagged:
        return "review"
    if hard_fail:
        return "below"
    if score >= STRONG_SCORE and not must_failed:
        return "strong"
    if score >= MAYBE_SCORE and not must_failed:
        return "maybe"
    return "below"


def load_banned_terms():
    path = ROOT / "data" / "banned_terms.json"
    return load_json(path) if path.exists() else {}


def load_env_file(path=".env"):
    """Read KEY=VALUE lines from a local .env into os.environ (existing variables win). Never prints values."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            if key and key not in os.environ:
                os.environ[key] = value.strip().strip('"').strip("'")
