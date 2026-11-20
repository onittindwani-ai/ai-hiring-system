"""Check a job post, message or scorecard for biased or risky wording (Python 3.9+, standard library only).

Usage:
    python3 tools/bias_check.py hiring/<role>/drafts/job-post.md --kind job-post
    python3 tools/bias_check.py hiring/<role>/drafts/message.md --kind message
    python3 tools/bias_check.py hiring/<role>/scorecard.json --kind scorecard

What it does:
    Flags, with line numbers and a plain fix:
      gendered words, age coded words, origin or language wording, "culture fit" style wording,
      hype words (ninja, rockstar), questions you should not ask, a job post with no pay range,
      and a long requirements list (more than 8 bullets, or 10 or more years asked).
    The word lists are in data/banned_terms.json. Add your own there.
    Exit 0 when there is nothing to fix or only low severity notes, 1 when a high or medium issue is found.

Guidance that names what NOT to ask (a "Never ask" list) would flag itself. Mark such a line with
    <!-- bias-check: guidance --> at the end of the line, or wrap several lines between
    <!-- bias-check: guidance-start --> and <!-- bias-check: guidance-end -->. Marked lines are skipped.
    A {{pay_range}} placeholder in a template counts as a pay range.

Limits:
    Word lists catch the usual suspects, not every case. A flag is a prompt to look, not a verdict.
    Some words are fine in context (a language the job truly needs). Not legal advice.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hlib  # noqa: E402

GROUPS = [
    ("unlawful_asks", "high", "question you should not ask"),
    ("origin_coded", "high", "origin or language wording"),
    ("gendered", "medium", "gendered wording"),
    ("age_coded", "medium", "age coded wording"),
    ("culture_fit", "medium", "culture fit wording"),
    ("hype", "low", "hype word"),
]
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}
CURRENCY_EXTRA = "".join(chr(code) for code in (0x20AC, 0xA3, 0x20B9))
PAY_RE = re.compile(
    r"\{\{\s*pay_range\s*\}\}|[$" + CURRENCY_EXTRA + "]\\s?\\d|\\b(?:usd|eur|gbp|inr|cad|aud)\\s?\\d|"
    r"\b(?:per|an|a)\s+(?:hour|year|month)\b|\blpa\b|\d\s?k\s*(?:-|to)\s*\d", re.IGNORECASE)
HEADING_RE = re.compile(
    r"^\s{0,3}(?:#+\s*)?(?:requirements|qualifications|what you bring|must have|you have|who you are|"
    r"what we(?:'|" + chr(0x2019) + r")re looking for|skills)\b", re.IGNORECASE)
BULLET_RE = re.compile(r"^\s*(?:[-*" + chr(0x2022) + r"]|\d+[.)])\s+")
YEARS_RE = re.compile(r"\b(\d{1,2})\s*\+?\s*(?:or more\s+)?years?\b", re.IGNORECASE)
OTHER_HEADING_RE = re.compile(r"^\s{0,3}#+\s|^\s*\*\*[^*]+\*\*:?\s*$|^[A-Z][^.]{0,40}:\s*$")
MAX_BULLETS = 8
MAX_YEARS = 10


def phrase_regex(phrase):
    """Whole word or phrase match, ignoring case. Spaces match any run of spaces."""
    parts = [re.escape(p) for p in str(phrase).split()]
    return re.compile(r"(?<![A-Za-z0-9])" + r"\s+".join(parts) + r"(?![A-Za-z0-9])", re.IGNORECASE)


def find_phrases(text, phrases):
    """List of (phrase, matched text) for each phrase found in `text`."""
    found = []
    for phrase in phrases:
        match = phrase_regex(phrase).search(text)
        if match:
            found.append((phrase, match.group(0)))
    return found


def _finding(line, severity, category, found, fix, where=None):
    item = {"line": line, "severity": severity, "category": category, "found": found, "fix": fix}
    if where:
        item["where"] = where
    return item


def check_lines(lines, kind="job-post", terms=None, labels=None):
    """Check a list of text lines. Returns a list of finding dicts sorted by line."""
    terms = terms if terms is not None else hlib.load_banned_terms()
    findings = []
    for number, text in enumerate(lines, start=1):
        where = labels[number - 1] if labels else None
        for key, severity, category in GROUPS:
            for phrase, shown in find_phrases(text, list((terms.get(key) or {}).keys())):
                findings.append(_finding(number, severity, category, shown, terms[key][phrase], where))
        if kind == "scorecard":
            for phrase, shown in find_phrases(text, terms.get("protected_traits", [])):
                findings.append(_finding(number, "high", "protected trait or proxy", shown,
                                         "A scorecard must only hold job related criteria. Remove it.", where))
    return findings


def check_job_post_extras(lines):
    """Pay range, requirement list length and years asked for."""
    findings = []
    text = "\n".join(lines)
    if not PAY_RE.search(text):
        findings.append(_finding(0, "medium", "no pay range found", "(whole post)",
                                 "Add the pay range. Many places require it, and candidates skip posts without it."))
    sections, current = [], None
    for number, line in enumerate(lines, start=1):
        if HEADING_RE.match(line):
            current = [number, 0]
            sections.append(current)
        elif current and OTHER_HEADING_RE.match(line):
            current = None
        elif current and BULLET_RE.match(line):
            current[1] += 1
    for start, bullets in sections:
        if bullets > MAX_BULLETS:
            findings.append(_finding(start, "medium", "long requirements list", "%d bullets" % bullets,
                                     "Keep 5 to 8 must haves. Move the rest to nice to have, or cut them."))
    for number, line in enumerate(lines, start=1):
        for match in YEARS_RE.finditer(line):
            if int(match.group(1)) >= MAX_YEARS:
                findings.append(_finding(number, "medium", "very long experience asked", match.group(0),
                                         "Ask for the skill, not a number of years. Long year counts can act as an age filter."))
    return findings


def flatten_json(value, path=""):
    """Yield (path, text) for every string in a JSON value."""
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from flatten_json(item, "%s.%s" % (path, key) if path else key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from flatten_json(item, "%s[%d]" % (path, index))


def skip_guidance(lines):
    """Blank out lines marked as guidance (a Never ask list), keeping line numbers."""
    out, inside = [], False
    for line in lines:
        if "bias-check: guidance-start" in line:
            inside = True
            out.append("")
        elif "bias-check: guidance-end" in line:
            inside = False
            out.append("")
        elif inside or "bias-check: guidance" in line:
            out.append("")
        else:
            out.append(line)
    return out


def check_text(text, kind="job-post", terms=None):
    lines = skip_guidance(text.splitlines())
    findings = check_lines(lines, kind, terms)
    if kind == "job-post":
        findings += check_job_post_extras(lines)
    return sorted(findings, key=lambda f: (f["line"], SEVERITY_ORDER[f["severity"]]))


def check_scorecard(card, terms=None):
    pairs = list(flatten_json(card))
    findings = check_lines([text for _, text in pairs], "scorecard", terms, [path for path, _ in pairs])
    return sorted(findings, key=lambda f: (f["line"], SEVERITY_ORDER[f["severity"]]))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check wording for bias and legal risk (not legal advice).")
    parser.add_argument("file")
    parser.add_argument("--kind", choices=["job-post", "message", "scorecard"], help="default: scorecard for .json, else job-post")
    args = parser.parse_args(argv)
    path = Path(args.file)
    if not path.is_file():
        print("File not found: %s" % path)
        return 1
    kind = args.kind or ("scorecard" if path.suffix.lower() == ".json" else "job-post")
    terms = hlib.load_banned_terms()
    if not terms:
        print("Could not find data/banned_terms.json. Restore it from the repo.")
        return 1
    try:
        if kind == "scorecard" or path.suffix.lower() == ".json":
            findings = check_scorecard(hlib.load_json(path), terms)
        else:
            findings = check_text(path.read_text(encoding="utf-8"), kind, terms)
    except (ValueError, OSError) as err:
        print("Could not read %s: %s" % (path, err))
        return 1
    print("bias_check: %s (kind %s)" % (path.name, kind))
    for item in findings:
        place = "line %d" % item["line"] if item["line"] else "post"
        extra = " (%s)" % item["where"] if item.get("where") else ""
        print("%s%s  %-6s %s: %s" % (place, extra, item["severity"].upper(), item["category"], item["found"]))
        print("    Fix: %s" % item["fix"])
    blocking = [f for f in findings if f["severity"] in ("high", "medium")]
    if not findings:
        print("Nothing found. (A word list check, not a legal review.)")
    else:
        print("\n%d finding(s), %d need a fix. Not legal advice." % (len(findings), len(blocking)))
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
