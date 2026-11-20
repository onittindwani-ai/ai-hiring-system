"""Validate a scorecard JSON file (Python 3.9+, standard library only).

Usage:
    python3 tools/validate_scorecard.py templates/scorecards/sales-development-rep.json
    python3 tools/validate_scorecard.py hiring/<role>/scorecard.json templates/scorecards/*.json

What it does:
    Checks a scorecard against the rules in this kit:
      required fields; 5 to 8 criteria; weights are whole numbers from 5 to 30 and add up to 100;
      at least 3 "must" criteria with a min_level from 1 to 3; exactly 5 level strings ("0 ..." to "4 ...");
      4 to 12 lowercase keywords per criterion; every interview question points at a real criterion;
      gates and deal breakers are complete; no protected trait or proxy used as a criterion
      (list in data/banned_terms.json); no long dashes.
    Prints OK per file, or ERROR and WARNING lines. Errors must be fixed, warnings are worth reading.
    Exit 0 if no file has an error, 1 if any has, 2 on usage error.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hlib  # noqa: E402
from bias_check import find_phrases  # noqa: E402

REQUIRED = ["version", "role_id", "title", "level", "mission", "outcomes_90_days", "criteria", "gates",
            "deal_breakers", "work_sample", "interview_questions", "red_flags", "sourcing_channels",
            "pay_research_hint", "automation_note"]
KNOWN_LEVELS = {"entry", "mid", "senior", "lead", "manager", "executive"}
ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
SLUG_RE = re.compile(r"^[a-z][a-z0-9\-]*$")
LONG_DASHES = (chr(0x2014), chr(0x2013))
YEARS_RE = re.compile(r"\b(\d{1,2})\s*\+?\s*years\b", re.IGNORECASE)


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _text(value):
    return value if isinstance(value, str) else ""


def _all_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _all_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _all_strings(item)


def _criterion_texts(criterion):
    parts = [_text(criterion.get("id")), _text(criterion.get("name")), _text(criterion.get("what_good_looks_like")),
             _text(criterion.get("jev_question"))]
    parts += [x for x in criterion.get("evidence_needed", []) if isinstance(x, str)]
    parts += [x for x in criterion.get("keywords", []) if isinstance(x, str)]
    return [p.replace("_", " ") for p in parts if p]


def _check_criterion(index, c, ids, errors, warnings):
    if not isinstance(c, dict):
        errors.append("criteria[%d] must be an object" % index)
        return None
    tag = "criteria[%d] (%s)" % (index, _text(c.get("id")) or "no id")
    for key in ("id", "name", "type", "weight", "what_good_looks_like", "evidence_needed", "keywords", "levels", "jev_question"):
        if key not in c:
            errors.append("%s is missing '%s'" % (tag, key))
    cid = _text(c.get("id"))
    if cid and not ID_RE.match(cid):
        errors.append("%s: id must be lowercase letters, digits and underscores" % tag)
    if cid in ids:
        errors.append("%s: duplicate id" % tag)
    ids.add(cid)
    kind = c.get("type")
    if kind not in ("must", "nice"):
        errors.append("%s: type must be 'must' or 'nice'" % tag)
    weight = c.get("weight")
    if not _is_int(weight) or not 5 <= weight <= 30:
        errors.append("%s: weight must be a whole number from 5 to 30" % tag)
    min_level = c.get("min_level")
    if kind == "must" and (not _is_int(min_level) or not 1 <= min_level <= 3):
        errors.append("%s: a must criterion needs min_level from 1 to 3" % tag)
    if kind == "nice" and min_level is not None and (not _is_int(min_level) or not 0 <= min_level <= 3):
        errors.append("%s: min_level must be a whole number from 0 to 3" % tag)
    levels = c.get("levels")
    if not isinstance(levels, list) or len(levels) != 5 or not all(isinstance(x, str) for x in levels):
        errors.append("%s: levels must be exactly 5 strings" % tag)
    else:
        for number, text in enumerate(levels):
            if not text.startswith("%d " % number):
                errors.append("%s: level %d must start with '%d ' (found %r)" % (tag, number, number, text[:12]))
    keywords = c.get("keywords")
    if not isinstance(keywords, list) or not 4 <= len(keywords) <= 12 or not all(isinstance(x, str) and x for x in keywords):
        errors.append("%s: keywords must be a list of 4 to 12 non empty strings" % tag)
    else:
        for word in keywords:
            if word != word.lower():
                errors.append("%s: keyword %r must be lowercase" % (tag, word))
        if len(set(keywords)) != len(keywords):
            warnings.append("%s: duplicate keywords" % tag)
    for key in ("name", "what_good_looks_like", "jev_question"):
        if key in c and not _text(c.get(key)).strip():
            errors.append("%s: '%s' is empty" % (tag, key))
    if not isinstance(c.get("evidence_needed"), list) or not c.get("evidence_needed"):
        errors.append("%s: evidence_needed must be a non empty list" % tag)
    return cid


def _check_bans(card, terms, errors, warnings):
    protected = list(terms.get("protected_traits", []))
    proxies = list(terms.get("proxies", []))
    trait_words = list(terms.get("trait_words", []))
    for index, c in enumerate(card.get("criteria", [])):
        if not isinstance(c, dict):
            continue
        tag = "criteria[%d] (%s)" % (index, _text(c.get("id")))
        name_words = " ".join([_text(c.get("id")).replace("_", " "), _text(c.get("name"))])
        for _, shown in find_phrases(name_words, trait_words):
            errors.append("%s: the criterion itself is about a protected trait: %r" % (tag, shown))
        for text in _criterion_texts(c):
            for _, shown in find_phrases(text, protected):
                errors.append("%s: %r is a protected trait or a proxy for one. Remove it." % (tag, shown))
            for _, shown in find_phrases(text, proxies):
                warnings.append("%s: %r can act as a proxy for a protected trait. Check it is truly job related." % (tag, shown))
            for match in YEARS_RE.finditer(text):
                if int(match.group(1)) >= 10:
                    warnings.append("%s: asking %s can act as an age filter. Ask for the skill instead." % (tag, match.group(0)))
    scan = []
    for gate in card.get("gates", []):
        scan += [("gate", _text(gate.get("id")).replace("_", " ")), ("gate", _text(gate.get("question")))] if isinstance(gate, dict) else []
    for db in card.get("deal_breakers", []):
        scan += [("deal breaker", _text(db.get("id")).replace("_", " ")), ("deal breaker", _text(db.get("description")))] if isinstance(db, dict) else []
    for q in card.get("interview_questions", []):
        scan += [("interview question", _text(q.get("question")))] if isinstance(q, dict) else []
    for where, text in scan:
        for _, shown in find_phrases(text, protected):
            errors.append("%s uses %r, a protected trait or proxy. Ask only about job related things." % (where, shown))
    soft = [("mission", _text(card.get("mission")))] + [("outcome", t) for t in card.get("outcomes_90_days", []) if isinstance(t, str)]
    soft += [("red flag", t) for t in card.get("red_flags", []) if isinstance(t, str)]
    for where, text in soft:
        for _, shown in find_phrases(text, protected):
            warnings.append("%s mentions %r. Check it is not a protected trait." % (where, shown))


def validate(card, terms=None):
    """Return (errors, warnings), two lists of plain sentences."""
    terms = terms if terms is not None else hlib.load_banned_terms()
    errors, warnings = [], []
    if not isinstance(card, dict):
        return ["The scorecard must be a JSON object."], []
    for key in REQUIRED:
        if key not in card:
            errors.append("Missing field '%s'." % key)
    if card.get("version") != 1:
        errors.append("version must be 1.")
    role = _text(card.get("role_id"))
    if role and not SLUG_RE.match(role):
        errors.append("role_id must be lowercase letters, digits and hyphens.")
    for key in ("title", "mission", "pay_research_hint", "automation_note"):
        if key in card and not _text(card.get(key)).strip():
            errors.append("'%s' is empty." % key)
    if card.get("level") not in KNOWN_LEVELS:
        warnings.append("level is %r; usual values are %s." % (card.get("level"), ", ".join(sorted(KNOWN_LEVELS))))
    if len(_text(card.get("mission")).split()) > 40:
        warnings.append("The mission should be one short sentence.")
    outcomes = card.get("outcomes_90_days")
    if not isinstance(outcomes, list) or not outcomes:
        errors.append("outcomes_90_days must be a list of 3 to 5 measurable outcomes.")
    elif not 3 <= len(outcomes) <= 5:
        warnings.append("outcomes_90_days should have 3 to 5 outcomes (has %d)." % len(outcomes))
    criteria = card.get("criteria")
    ids = set()
    if not isinstance(criteria, list):
        errors.append("criteria must be a list.")
        criteria = []
    if not 5 <= len(criteria) <= 8:
        errors.append("A scorecard needs 5 to 8 criteria (has %d)." % len(criteria))
    for index, c in enumerate(criteria):
        _check_criterion(index, c, ids, errors, warnings)
    dicts = [c for c in criteria if isinstance(c, dict)]
    total = sum(c["weight"] for c in dicts if _is_int(c.get("weight")))
    if total != 100:
        errors.append("Weights must add up to 100 (they add up to %d)." % total)
    if sum(1 for c in dicts if c.get("type") == "must") < 3:
        errors.append("At least 3 criteria must have type 'must'.")
    _check_extras(card, ids, dicts, errors, warnings)
    _check_bans(card, terms, errors, warnings)
    for text in _all_strings(card):
        if any(d in text for d in LONG_DASHES):
            errors.append("A long dash was found in %r. Use a comma, colon or period instead." % text[:40])
            break
    return errors, warnings


def _check_extras(card, ids, dicts, errors, warnings):
    seen = set(ids)
    for kind, key, needed in (("gates", "gates", ("id", "question", "kind")),
                              ("deal breaker", "deal_breakers", ("id", "description", "job_related_reason"))):
        items = card.get(key, [])
        if not isinstance(items, list):
            errors.append("%s must be a list (it may be empty)." % key)
            continue
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append("%s[%d] must be an object." % (key, i))
                continue
            for field in needed:
                if not _text(item.get(field)).strip():
                    errors.append("%s[%d] is missing '%s'." % (key, i, field))
            if key == "gates" and item.get("kind") not in ("hard", "soft"):
                errors.append("gates[%d]: kind must be 'hard' or 'soft'." % i)
            if _text(item.get("id")) in seen:
                errors.append("%s[%d]: id %r is already used." % (key, i, item.get("id")))
            seen.add(_text(item.get("id")))
    sample = card.get("work_sample")
    if not isinstance(sample, dict):
        errors.append("work_sample must be an object.")
    else:
        for field in ("title", "brief", "how_to_score"):
            if not _text(sample.get(field)).strip():
                warnings.append("work_sample.%s is empty." % field)
        if not _is_int(sample.get("time_limit_minutes")) or not 10 <= sample.get("time_limit_minutes", 0) <= 180:
            warnings.append("work_sample.time_limit_minutes should be a whole number from 10 to 180.")
    questions = card.get("interview_questions", [])
    asked = set()
    if not isinstance(questions, list):
        errors.append("interview_questions must be a list.")
        return
    for i, q in enumerate(questions):
        if not isinstance(q, dict):
            errors.append("interview_questions[%d] must be an object." % i)
            continue
        if q.get("criterion_id") not in ids:
            errors.append("interview_questions[%d]: criterion_id %r is not a criterion." % (i, q.get("criterion_id")))
        asked.add(q.get("criterion_id"))
        if not _text(q.get("question")).strip():
            errors.append("interview_questions[%d] has no question." % i)
        for field in ("good_answer_signs", "weak_answer_signs"):
            if not isinstance(q.get(field), list) or not q.get(field):
                warnings.append("interview_questions[%d] has no %s." % (i, field))
    if len(questions) < 5:
        warnings.append("Fewer than 5 interview questions (has %d)." % len(questions))
    for c in dicts:
        if c.get("type") == "must" and c.get("id") not in asked:
            warnings.append("The must criterion %r has no interview question." % c.get("id"))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate scorecard JSON files.")
    parser.add_argument("files", nargs="+")
    args = parser.parse_args(argv)
    terms = hlib.load_banned_terms()
    if not terms:
        print("Could not find data/banned_terms.json. Restore it from the repo.")
        return 1
    failed = False
    for name in args.files:
        path = Path(name)
        try:
            errors, warnings = validate(hlib.load_json(path), terms)
        except (OSError, ValueError) as err:
            print("ERROR %s: cannot read it (%s)" % (name, err))
            failed = True
            continue
        for line in errors:
            print("ERROR %s: %s" % (name, line))
        for line in warnings:
            print("WARNING %s: %s" % (name, line))
        if errors:
            failed = True
        else:
            print("OK %s (%d warning(s))" % (name, len(warnings)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
