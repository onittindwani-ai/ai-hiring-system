"""Blind a resume before it is scored (Python 3.9+, standard library only).

Usage:
    python3 tools/redact.py resume.txt                         # prints the redacted text
    python3 tools/redact.py resume.txt --out resume.redacted.txt --names "Priya Rao,Priya"
    from redact import redact_text, redact_report

What it does:
    Removes or replaces things that identify a person or can hint at a protected trait, so the score
    depends on the work and not on who wrote it:
      emails, phone numbers, web links (kept as [link]), street addresses, dates of birth and ages,
      honorifics (Mr, Mrs, Ms, Miss, Mx), gendered pronouns (replaced with they, them, their),
      family status words, photo mentions, labelled fields such as "Gender:" or "Nationality:",
      and the names you give with --names (the candidate name is always passed by score_candidates.py).

Limits (read these):
    It is pattern based. It will miss things written in unusual ways, in other languages, or inside
    images and PDFs that were not turned into text. It does NOT remove schools, employers, graduation
    years, city names or job dates, because the scorer needs the work history, and these can still hint at
    age, origin or gender. Pronoun swaps can leave small grammar slips ("they leads"). Always keep a person
    in the loop: redaction lowers bias, it does not remove it.
"""
import argparse
import re
import sys
from pathlib import Path

LABELLED = re.compile(
    r"^[ \t]*(?:gender|sex|nationality|marital status|religion|date of birth|dob|age|"
    r"photo|ethnicity|caste|passport(?: number)?|visa status)\s*:.*$", re.IGNORECASE | re.MULTILINE)
EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
URL = re.compile(r"(?:https?://|www\.)[^\s<>()\[\]]+|\b(?:[a-z0-9\-]+\.)+(?:com|org|net|io|dev|co|ai|me|app|test)(?:/[^\s<>()\[\]]*)?",
                 re.IGNORECASE)
PHONES = [re.compile(rx) for rx in (
    r"(?<!\w)\+\d{1,3}[\s.\-]?\(?\d{1,4}\)?(?:[\s.\-]?\d{2,4}){2,4}(?!\w)",
    r"(?<!\w)\(\d{2,4}\)\s?\d{3,4}[\s.\-]?\d{3,4}(?!\w)",
    r"(?<!\w)\d{3}[\s.\-]\d{3,4}[\s.\-]\d{3,4}(?!\w)",
    r"(?<!\w)\d{3}[\s.\-]\d{4}(?!\w)",
    r"(?<!\w)\d{5}\s\d{5}(?!\w)",
    r"(?<!\w)\d{10,11}(?!\w)",
)]
ADDRESS = re.compile(
    r"\b\d{1,5}\s+(?:[A-Z][A-Za-z]*\.?\s+){1,3}(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Boulevard|Blvd|Drive|Dr|Court|Ct|Way|Place|Pl)\b\.?")
DATE_TOKEN = (r"(?:\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4}|\d{4}[/.\-]\d{1,2}[/.\-]\d{1,2}|"
              r"(?:\d{1,2}(?:st|nd|rd|th)?\s+)?[A-Za-z]{3,9}\.?\s+(?:\d{1,2}(?:st|nd|rd|th)?,?\s+)?\d{4}|\d{4})")
DOB = re.compile(r"\b(?:dob|d\.o\.b\.?|date of birth|born(?:\s+on|\s+in)?)\s*[:\-]?\s*" + DATE_TOKEN, re.IGNORECASE)
AGE = re.compile(r"\b(?:aged?\s+\d{2}|\d{2}\s*(?:years?|yrs?)[\s\-]*old|\d{2}\s*year[\s\-]old)\b", re.IGNORECASE)
PHOTO = re.compile(r"\b(?:profile\s+)?(?:photo(?:graph)?|headshot|selfie)s?\b", re.IGNORECASE)
HONORIFIC = re.compile(r"\b(?:Mr|Mrs|Ms|Mx)\b\.?\s*|\bMiss\s+(?=[A-Z])")
FAMILY = re.compile(
    r"\b(?:(?:married|unmarried|divorced|widowed)(?:\s+(?:with|and)\s+(?:\w+\s+){1,2}(?:kids|children|sons|daughters))?|"
    r"husband|wife|pregnant|pregnancy|maternity|paternity|"
    r"single (?:mother|father|parent)|mother of|father of|my (?:kids|children|son|daughter))\b", re.IGNORECASE)
COMBINED = [
    (re.compile(r"\b(?:he|she)\s*(?:/|or)\s*(?:she|he)\b|\bs/he\b", re.IGNORECASE), "they"),
    (re.compile(r"\b(?:his|her)\s*(?:/|or)\s*(?:her|his)\b", re.IGNORECASE), "their"),
    (re.compile(r"\b(?:him|her)\s*(?:/|or)\s*(?:her|him)\b", re.IGNORECASE), "them"),
]
PRONOUN = re.compile(r"\b(he|she|him|her|his|hers|himself|herself)\b", re.IGNORECASE)
SIMPLE = {"he": "they", "she": "they", "him": "them", "his": "their", "hers": "theirs",
          "himself": "themselves", "herself": "themselves"}
OBJECT_FOLLOWERS = set("and or to for at in on with by as from of about that when if so but into over after before than then a an the this these those".split())
VERB_FIX = {"is": "are", "was": "were", "has": "have", "does": "do", "isn't": "aren't",
            "wasn't": "weren't", "hasn't": "haven't", "doesn't": "don't"}


def _match_case(original, replacement):
    return replacement.capitalize() if original[:1].isupper() else replacement


def _swap_pronouns(text):
    for rx, word in COMBINED:
        text = rx.sub(lambda m, w=word: _match_case(m.group(0), w), text)

    def replace(match):
        word = match.group(1).lower()
        if word == "her":
            rest = text_ref[match.end():]
            follow = re.match(r"\s+([A-Za-z']+)", rest)
            ends = not follow or re.match(r"\s*[,.;:!?)\n]", rest) is not None
            new = "them" if ends or (follow and follow.group(1).lower() in OBJECT_FOLLOWERS) else "their"
        else:
            new = SIMPLE[word]
        return _match_case(match.group(1), new)

    text_ref = text
    swapped = PRONOUN.sub(replace, text)
    return re.sub(r"\b([Tt]hey)\s+(is|was|has|does|isn't|wasn't|hasn't|doesn't)\b",
                  lambda m: "%s %s" % (m.group(1), VERB_FIX[m.group(2).lower()]), swapped)


def _name_parts(names):
    full, parts = [], []
    for name in names:
        name = str(name).strip()
        if len(name) < 2:
            continue
        full.append(name)
        parts.extend(p for p in re.split(r"\s+", name) if len(p) >= 2)
    return sorted(set(full), key=len, reverse=True), sorted(set(parts), key=len, reverse=True)


def redact_report(text, names=()):
    """Return (redacted_text, counts). `counts` says how many of each kind were replaced."""
    counts = {}

    def sub(label, rx, repl, value):
        value, n = rx.subn(repl, value)
        if n:
            counts[label] = counts.get(label, 0) + n
        return value

    text = str(text or "")
    text = sub("labelled_fields", LABELLED, "[removed]", text)
    text = sub("email", EMAIL, "[email]", text)
    text = sub("link", URL, "[link]", text)
    for rx in PHONES:
        text = sub("phone", rx, "[phone]", text)
    text = sub("address", ADDRESS, "[address]", text)
    text = sub("birth_date", DOB, "[date of birth removed]", text)
    text = sub("age", AGE, "[age removed]", text)
    text = sub("photo", PHOTO, "[image]", text)
    text = sub("honorific", HONORIFIC, "", text)
    text = sub("family_status", FAMILY, "[family detail removed]", text)
    full, parts = _name_parts(names)
    for name in full:
        text = sub("name", re.compile(r"\b%s\b" % re.escape(name), re.IGNORECASE), "[name]", text)
    for part in parts:
        text = sub("name", re.compile(r"\b%s\b" % re.escape(part)), "[name]", text)
    before = len(PRONOUN.findall(text)) + sum(len(rx.findall(text)) for rx, _ in COMBINED)
    text = _swap_pronouns(text)
    if before:
        counts["pronoun"] = before
    return text, counts


def redact_text(text, names=()):
    """The redacted text only. See redact_report for the counts."""
    return redact_report(text, names)[0]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Remove identifying details from a resume text.")
    parser.add_argument("input", help="a text file")
    parser.add_argument("--out", help="write the result here instead of printing it")
    parser.add_argument("--names", default="", help='names to remove, comma separated, for example "Priya Rao,Priya"')
    args = parser.parse_args(argv)
    path = Path(args.input)
    if not path.is_file():
        print("File not found: %s" % path)
        return 1
    names = [n for n in args.names.split(",") if n.strip()]
    text, counts = redact_report(path.read_text(encoding="utf-8"), names)
    summary = ", ".join("%s %d" % (k, v) for k, v in sorted(counts.items())) or "nothing found to remove"
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")
        print("Wrote %s (%s). Limits: see the top of tools/redact.py." % (args.out, summary))
    else:
        print(text)
        print("\n[redacted: %s]" % summary, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
