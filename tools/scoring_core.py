"""Shared scoring maths for tools/score_candidates.py (Python 3.9+, standard library only).

Usage:
    from scoring_core import prepare, finish_record

What it does:
    prepare(): blinds a candidate text (redaction), finds and cuts out wording aimed at an AI screener.
    finish_record(): turns criterion levels, gate answers and deal breaker answers into the score record from
    the kit spec: weighted score, flags, tier (strong, maybe, review, below), needs_human and plain reasons.
    It never writes "rejected".
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hlib  # noqa: E402
from injection_check import find_injection, strip_injection  # noqa: E402
from redact import redact_text  # noqa: E402


def known_names(candidate, extra):
    """Names to blind: the candidate name, its parts, and any names from --names-file."""
    names = [str(candidate.get("name", "")).strip()] + list(extra)
    email = str(candidate.get("email", ""))
    if "@" in email:
        names.append(email.split("@")[0].replace(".", " ").replace("_", " "))
    return [n for n in names if len(n) >= 2]


def prepare(candidate, extra_names, redact):
    """Return (text to score, injection matches). Injected wording is cut out of the text."""
    raw = hlib.candidate_text(candidate)
    matches = find_injection(raw)
    text = redact_text(raw, known_names(candidate, extra_names)) if redact else raw
    clean, _ = strip_injection(text)
    return clean, matches


def _gate_flag_text(gate):
    return gate.get("question") or gate["id"]


def finish_record(scorecard, candidate, engine, criteria, gates, deal_breakers, injection, unknown_gates_review=True):
    """Apply the spec maths: weighted score, flags, tier, needs_human, reasons.
    unknown_gates_review=False keeps the gate_unknown flag and needs_human but does not force the tier review."""
    levels = {cid: int(v["level"]) for cid, v in criteria.items()}
    score = hlib.weighted_score(scorecard, levels)
    failed = hlib.must_failures(scorecard, levels)
    musts = [c for c in scorecard["criteria"] if c.get("type") == "must"]
    must_conf = [criteria[c["id"]]["confidence"] for c in musts if c["id"] in criteria]
    low_conf = any(conf < hlib.CONFIDENCE_LOW for conf in must_conf)
    hard_unknown = [g for g in scorecard.get("gates", []) if g.get("kind") == "hard" and gates.get(g["id"]) == "unknown"]
    any_unknown = [g for g in scorecard.get("gates", []) if gates.get(g["id"]) == "unknown"]
    gate_no = [g for g in scorecard.get("gates", []) if gates.get(g["id"]) == "no"]
    db_yes = [d for d in scorecard.get("deal_breakers", []) if deal_breakers.get(d["id"]) == "yes"]
    db_unknown = [d for d in scorecard.get("deal_breakers", []) if deal_breakers.get(d["id"]) == "unknown"]
    flags = []
    if injection:
        flags.append("prompt_injection_suspected")
    if low_conf:
        flags.append("low_confidence")
    if any_unknown:
        flags.append("gate_unknown")
    if failed:
        flags.append("must_have_missing")
    flagged = bool(injection) or low_conf or (bool(hard_unknown) and unknown_gates_review)
    tier = hlib.tier_for(score, failed, bool(gate_no or db_yes), flagged)
    lowest = min(must_conf) if must_conf else 1.0
    needs_human = (tier == "review" or (tier in ("strong", "maybe") and lowest < hlib.CONFIDENCE_OK)
                   or bool(any_unknown or gate_no or db_yes or db_unknown))
    reasons = build_reasons(scorecard, criteria, levels, failed, injection, low_conf, any_unknown, gate_no, db_yes,
                            score, tier)
    return {"candidate_id": candidate.get("candidate_id"), "role_id": scorecard["role_id"], "engine": engine,
            "criteria": criteria, "gates": gates, "deal_breakers": deal_breakers, "weighted_score": score,
            "tier": tier, "needs_human": needs_human, "reasons": reasons, "flags": flags}


def build_reasons(scorecard, criteria, levels, failed, injection, low_conf, unknown, gate_no, db_yes, score, tier):
    by_id = {c["id"]: c for c in scorecard["criteria"]}
    reasons = []
    strongest = sorted((c for c in scorecard["criteria"] if levels[c["id"]] >= 2),
                       key=lambda c: -c["weight"] * levels[c["id"]])[:2]
    for c in strongest:
        reasons.append("Shows %s (level %d of 4)." % (c["name"].lower(), levels[c["id"]]))
    for cid in failed:
        reasons.append("Must have not shown yet: %s (level %d, needs %d)." % (
            by_id[cid]["name"].lower(), levels[cid], by_id[cid].get("min_level", 1)))
    if injection:
        reasons.append("The text has wording aimed at an AI screener. It was ignored. A person should read it.")
    if low_conf:
        reasons.append("Low confidence on a must have. The text may be too thin to judge.")
    for g in unknown:
        reasons.append("Could not tell: %s" % _gate_flag_text(g))
    for g in gate_no:
        reasons.append("Answered no to: %s A person confirms before any decision." % _gate_flag_text(g))
    for d in db_yes:
        reasons.append("Deal breaker shown: %s A person confirms before any decision." % d["description"])
    if tier == "below":
        reasons.append("Not shortlisted now (score %.1f). A person decides every no." % score)
    return reasons
