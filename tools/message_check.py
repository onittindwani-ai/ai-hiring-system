"""Message checker: catches the mistakes that make a hiring message embarrassing or risky.

Usage:
    python3 tools/message_check.py hiring/<role>/drafts/first-message.md --kind cold
    python3 tools/message_check.py <file> --kind candidate --channel email
    python3 tools/message_check.py templates/messages/cold-email.md --kind cold --template

What it does:
    Reads a message and reports ERROR or WARN lines with the line number and a plain fix.
    Checks: unfilled placeholders in both styles ({{name}} and [NAME]), length limits (LinkedIn
    connection note 300 characters, email subject 60, SMS 160), a starting list of spam words,
    a missing STOP line on cold messages ("Reply STOP"), phrases that sound like an invented
    personal fact, and dashes. Optional header lines at the top of the file: "Channel: email"
    (or linkedin_connection, linkedin_message, sms) and "Subject: ...". Use --template for a
    template that still contains {{variables}} on purpose. Exit code 1 when any ERROR is found.
    It never sends anything.
"""
import argparse
import re
import sys
from pathlib import Path

LIMITS = {"linkedin_connection": 300, "sms": 160}
SUBJECT_LIMIT = 60
CHANNELS = ["email", "linkedin_connection", "linkedin_message", "sms", "dm"]
# Starting list, edit freely. Not a deliverability guarantee.
SPAM_WORDS = ["act now", "limited time", "100% free", "guaranteed", "risk free", "no obligation", "click here",
              "winner", "congratulations", "make money", "earn extra", "urgent", "once in a lifetime", "buy now"]
CLAIM_PHRASES = ["loved your recent post", "love your recent post", "saw your recent post", "impressed by your recent",
                 "came across your profile", "i noticed you", "your recent work", "your latest article"]
DASH_CHARS = "\u2012\u2013\u2014\u2015\u2212"
DOUBLE_VAR_RE = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")
BRACKET_RE = re.compile(r"\[([^\]\n]{1,60})\](?!\()")
HEADER_RE = re.compile(r"^(channel|subject)\s*:\s*(.*)$", re.IGNORECASE)
STOP_RE = re.compile(r"reply\s+stop|text\s+stop|send\s+stop", re.IGNORECASE)


def split_message(text):
    """Return (headers dict, body lines with original line numbers)."""
    headers, body = {}, []
    in_header = True
    for number, line in enumerate(text.splitlines(), start=1):
        found = HEADER_RE.match(line.strip()) if in_header else None
        if found:
            headers[found.group(1).lower()] = (found.group(2).strip(), number)
            continue
        if line.strip():
            in_header = False
        body.append((number, line))
    return headers, body


def check_message(text, kind="candidate", channel=None, template=False):
    """Return a list of (level, line_number_or_0, message)."""
    findings = []
    headers, body = split_message(text)
    channel = channel or (headers.get("channel", ("", 0))[0] or None)
    if channel and channel not in CHANNELS:
        findings.append(("WARN", headers.get("channel", ("", 0))[1], "Unknown channel '%s'. Known: %s." % (channel, ", ".join(CHANNELS))))
    for number, line in body:
        if not template:
            for match in DOUBLE_VAR_RE.finditer(line):
                findings.append(("ERROR", number, "Unfilled placeholder {{%s}}. Fill it with a real, checked fact." % match.group(1)))
        for match in BRACKET_RE.finditer(line):
            if re.search(r"[A-Za-z]", match.group(1)):
                findings.append(("ERROR", number, "Unfilled placeholder [%s]. Replace it or delete the line." % match.group(1)))
        lowered = line.lower()
        for word in SPAM_WORDS:
            if word in lowered:
                findings.append(("WARN", number, "Spam style phrase '%s'. Say it more plainly." % word))
        for phrase in CLAIM_PHRASES:
            if phrase in lowered:
                findings.append(("WARN", number, "'%s' sounds like a personal fact. Only keep it if it is true and you can name the exact thing." % phrase))
        if line.count("!") > 1:
            findings.append(("WARN", number, "More than one exclamation mark. Use at most one."))
        if any(ch in line for ch in DASH_CHARS):
            findings.append(("ERROR", number, "Dash character found. Use a comma, colon, period or parentheses."))
        elif " - " in line:
            findings.append(("WARN", number, "A spaced hyphen looks like a dash. Use a comma or a full stop."))
    subject = headers.get("subject")
    if subject and len(subject[0]) > SUBJECT_LIMIT:
        findings.append(("WARN", subject[1], "Subject is %d characters, limit %d. Shorten it." % (len(subject[0]), SUBJECT_LIMIT)))
    if subject and any(ch in subject[0] for ch in DASH_CHARS):
        findings.append(("ERROR", subject[1], "Dash character in the subject."))
    body_text = "\n".join(line for _, line in body).strip()
    if channel in LIMITS and len(body_text) > LIMITS[channel]:
        findings.append(("ERROR", 0, "%s message is %d characters, limit %d." % (channel, len(body_text), LIMITS[channel])))
    if kind == "cold" and not STOP_RE.search(body_text):
        findings.append(("ERROR", 0, "A cold message needs an opt out line, for example 'Reply STOP and I will not write again.'"))
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check a hiring message before you send it")
    parser.add_argument("file")
    parser.add_argument("--kind", choices=["cold", "candidate"], default="candidate")
    parser.add_argument("--channel", choices=CHANNELS)
    parser.add_argument("--template", action="store_true", help="allow {{variables}} (this file is a template)")
    args = parser.parse_args(argv)
    path = Path(args.file)
    if not path.exists():
        print("File not found: %s" % path)
        return 1
    findings = check_message(path.read_text(encoding="utf-8"), args.kind, args.channel, args.template)
    if not findings:
        print("OK: %s has no problems found. A person still reads it before it is sent." % path.name)
        return 0
    for level, number, message in findings:
        print("%s%s: %s" % (level, (" line %d" % number) if number else "", message))
    errors = sum(1 for f in findings if f[0] == "ERROR")
    print("%d error(s), %d warning(s)." % (errors, len(findings) - errors))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
