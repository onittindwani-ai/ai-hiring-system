"""Message renderer: fills {{variables}} in a message template. It never sends anything.

Usage:
    python3 tools/render_message.py templates/messages/cold-email.md --vars vars.json
    python3 tools/render_message.py <template.md> --vars vars.json --out hiring/<role>/drafts/first-message.md
    python3 tools/render_message.py <template.md> --vars vars.json --check cold

What it does:
    Replaces every {{name}} (spaces inside the braces are fine) with the matching value from the
    JSON file. If a variable is missing or empty, it stops and lists them all, so you never send
    "Hi {{candidate_first_name}}". Variables that are not used are ignored. With --check it runs
    tools/message_check.py on the result and stops on errors. Typical variables:
    candidate_first_name, role_title, company_name, recruiter_name, booking_link, pay_range,
    start_date, specific_detail (a real detail someone verified, never an invented one).
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from message_check import check_message  # noqa: E402

VAR_RE = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")


def find_variables(template):
    seen = []
    for match in VAR_RE.finditer(template):
        if match.group(1) not in seen:
            seen.append(match.group(1))
    return seen


def render(template, values):
    """Return (text, missing). `missing` lists variables with no value; text is unchanged for those."""
    missing = [name for name in find_variables(template) if not str(values.get(name, "")).strip()]
    if missing:
        return template, missing
    return VAR_RE.sub(lambda m: str(values[m.group(1)]).strip(), template), []


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fill a message template with real values")
    parser.add_argument("template")
    parser.add_argument("--vars", required=True, help="JSON file with the values")
    parser.add_argument("--out")
    parser.add_argument("--check", choices=["cold", "candidate"], help="also run the message checker")
    args = parser.parse_args(argv)
    template_path, vars_path = Path(args.template), Path(args.vars)
    for path in (template_path, vars_path):
        if not path.exists():
            print("File not found: %s" % path)
            return 1
    try:
        values = json.loads(vars_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print("The variables file is not valid JSON: %s" % exc)
        return 1
    if not isinstance(values, dict):
        print("The variables file must be a JSON object like {\"role_title\": \"Bookkeeper\"}.")
        return 1
    text, missing = render(template_path.read_text(encoding="utf-8"), values)
    if missing:
        print("Missing values, nothing was written: %s" % ", ".join(missing))
        return 1
    if args.check:
        errors = [f for f in check_message(text, args.check) if f[0] == "ERROR"]
        if errors:
            for _, number, message in errors:
                print("ERROR%s: %s" % ((" line %d" % number) if number else "", message))
            print("The message was not written because the check found errors.")
            return 1
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")
        print("Wrote %s (a draft: nothing was sent)." % args.out)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
