"""Prospect list: people you found from public sources and may contact, kept minimal and fair.

Usage:
    python3 tools/prospects.py init <role>
    python3 tools/prospects.py add --role <role> --name "Name" --url https://example.com/p/1
        [--headline "..."] [--location "City"] [--source google_search] [--fit-note "..."] [--notes "..."]
    python3 tools/prospects.py import --role <role> <file.csv|file.txt> [--source google_search]
    python3 tools/prospects.py dedupe --role <role>
    python3 tools/prospects.py mark --role <role> <prospect_id> <status>
    python3 tools/prospects.py stats --role <role>
    python3 tools/prospects.py contactable --role <role>
    (every command also accepts --base DIR, default "hiring", or --file PATH to a prospects.csv;
     add and import accept --allow-email, default off)

What it does:
    Keeps hiring/<role>/prospects.csv with minimal data: a public URL and a work related fit note.
    It removes duplicates by public URL and by lower case name plus location, refuses any row that
    carries a private email address unless you pass --allow-email, and never lists a person who is
    stopped or opted out as contactable. A text import reads a pasted file of URLs or lines like
    "Name | headline | location | https://url". It never contacts anyone and never visits a website.
"""
import argparse
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hlib import (CONTACT_STATUSES, PROSPECT_COLUMNS, PROSPECT_SOURCES, read_csv,  # noqa: E402
                  today_iso, write_csv)

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
URL_RE = re.compile(r"https?://[^\s|,;<>\"')]+")
URL_ALIASES = ("public_url", "url", "link", "profile", "profile_url")
FIELD_ALIASES = {"name": ("name", "full_name"), "headline": ("headline", "title", "position"),
                 "location": ("location", "city"), "fit_note": ("fit_note", "fit", "note"),
                 "source": ("source",), "notes": ("notes",)}


def role_file(args):
    if getattr(args, "file", None):
        return Path(args.file)
    if not getattr(args, "role", None):
        raise SystemExit("Tell me which role: add --role <role> (or --file path/to/prospects.csv).")
    return Path(args.base) / args.role / "prospects.csv"


def normalize_url(url):
    parsed = urlparse(str(url).strip().lower())
    host = parsed.netloc[4:] if parsed.netloc.startswith("www.") else parsed.netloc
    return (host + parsed.path).rstrip("/")


def dedupe_keys(row):
    keys = []
    if row.get("public_url"):
        keys.append("url:" + normalize_url(row["public_url"]))
    if row.get("name"):
        keys.append("name:%s|%s" % (row["name"].strip().lower(), (row.get("location") or "").strip().lower()))
    return keys


def has_private_email(row):
    return any(EMAIL_RE.search(str(value or "")) for value in row.values())


def is_contactable(row):
    return (row.get("opt_out", "no").lower() != "yes"
            and row.get("contact_status", "not_contacted") not in ("stopped", "not_interested"))


def merge_rows(existing, incoming):
    """Add incoming rows that are not duplicates. Returns (rows, added, skipped_duplicates)."""
    seen = {key for row in existing for key in dedupe_keys(row)}
    rows, added, skipped = list(existing), 0, 0
    for row in incoming:
        keys = dedupe_keys(row)
        if any(key in seen for key in keys):
            skipped += 1
            continue
        seen.update(keys)
        rows.append(row)
        added += 1
    return rows, added, skipped


def next_ids(rows, count):
    numbers = [int(m.group(1)) for r in rows for m in [re.fullmatch(r"P(\d+)", r.get("prospect_id", ""))] if m]
    start = max(numbers, default=0)
    return ["P%03d" % (start + i + 1) for i in range(count)]


def make_row(role, fields, source, allow_email):
    """Build one prospect row, or return (None, reason)."""
    url = fields.get("public_url", "").strip()
    if not url or not URL_RE.fullmatch(url):
        return None, "no public http(s) URL"
    if source not in PROSPECT_SOURCES:
        return None, "unknown source '%s' (use one of: %s)" % (source, ", ".join(PROSPECT_SOURCES))
    row = {"prospect_id": "", "role_id": role, "name": fields.get("name", "").strip(),
           "headline": fields.get("headline", "").strip(), "location": fields.get("location", "").strip(),
           "public_url": url, "source": source, "found_on": today_iso(), "fit_note": fields.get("fit_note", "").strip(),
           "contact_status": "not_contacted", "opt_out": "no", "notes": fields.get("notes", "").strip()}
    if has_private_email(row) and not allow_email:
        return None, "contains an email address (use --allow-email only if the person published it for work contact)"
    return row, None


def parse_csv_rows(path):
    out = []
    for raw in read_csv(path):
        lowered = {(k or "").strip().lower(): (v or "") for k, v in raw.items()}
        fields = {"public_url": next((lowered[a] for a in URL_ALIASES if lowered.get(a)), "")}
        for target, aliases in FIELD_ALIASES.items():
            fields[target] = next((lowered[a] for a in aliases if lowered.get(a)), "")
        for key in lowered:
            if "email" in key and lowered[key]:
                fields["notes"] = (fields.get("notes", "") + " " + lowered[key]).strip()
        out.append(fields)
    return out


def parse_text_rows(path):
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        found = URL_RE.search(line)
        if not line or line.startswith("#") or not found:
            continue
        url = found.group(0)
        rest = (line[:found.start()] + " " + line[found.end():]).strip(" |,;-")
        parts = [p.strip() for p in rest.split("|") if p.strip()]
        out.append({"public_url": url, "name": parts[0] if parts else "",
                    "headline": parts[1] if len(parts) > 1 else "",
                    "location": parts[2] if len(parts) > 2 else "",
                    "fit_note": parts[3] if len(parts) > 3 else ""})
    return out


def do_import(args, path, rows):
    source_file = Path(args.input)
    if not source_file.exists():
        print("File not found: %s" % source_file)
        return 1
    parsed = parse_csv_rows(source_file) if source_file.suffix.lower() == ".csv" else parse_text_rows(source_file)
    built, refused = [], []
    for fields in parsed:
        source = fields.get("source") or args.source
        row, reason = make_row(args.role or path.parent.name, fields, source, args.allow_email)
        if row:
            built.append(row)
        else:
            refused.append("%s: %s" % (fields.get("name") or fields.get("public_url") or "(blank)", reason))
    merged, added, skipped = merge_rows(rows, built)
    ids = iter(next_ids(merged, added))
    merged = [dict(r, prospect_id=next(ids)) if not r.get("prospect_id") else r for r in merged]
    write_csv(path, PROSPECT_COLUMNS, merged)
    print("Imported %d new, skipped %d duplicates, refused %d." % (added, skipped, len(refused)))
    for item in refused:
        print("  refused: " + item)
    return 0


def do_mark(args, path, rows):
    if args.status not in CONTACT_STATUSES:
        print("Unknown status '%s'. Use one of: %s." % (args.status, ", ".join(CONTACT_STATUSES)))
        return 1
    match = [r for r in rows if r["prospect_id"] == args.prospect_id]
    if not match:
        print("No prospect with id %s." % args.prospect_id)
        return 1
    if not is_contactable(match[0]) and args.status in ("contacted", "replied", "interested"):
        print("%s opted out or asked to stop. They stay off the contact list." % args.prospect_id)
        return 1
    updated = []
    for row in rows:
        if row["prospect_id"] == args.prospect_id:
            row = dict(row, contact_status=args.status)
            if args.status == "stopped":
                row["opt_out"] = "yes"
        updated.append(row)
    write_csv(path, PROSPECT_COLUMNS, updated)
    print("%s is now %s%s." % (args.prospect_id, args.status, " (opt out recorded)" if args.status == "stopped" else ""))
    return 0


def stats_text(rows):
    lines = ["Prospects: %d" % len(rows), "", "By source:"]
    lines += ["  %-14s %d" % (k, v) for k, v in sorted(Counter(r["source"] for r in rows).items())] or ["  (none)"]
    lines += ["", "By contact status:"]
    lines += ["  %-14s %d" % (k, v) for k, v in sorted(Counter(r["contact_status"] for r in rows).items())] or ["  (none)"]
    opted = sum(1 for r in rows if r.get("opt_out", "").lower() == "yes")
    lines += ["", "Opted out: %d" % opted,
              "Contactable now (not stopped, not opted out, not declined): %d" % sum(1 for r in rows if is_contactable(r))]
    return "\n".join(lines)


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--role")
    common.add_argument("--base", default="hiring")
    common.add_argument("--file")
    parser = argparse.ArgumentParser(description="Prospect list tool")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", parents=[common]).add_argument("init_role", nargs="?")
    p_add = sub.add_parser("add", parents=[common])
    p_add.add_argument("--name", default="")
    p_add.add_argument("--url", default="")
    for key in ("headline", "location", "fit-note", "notes"):
        p_add.add_argument("--" + key, default="")
    p_add.add_argument("--source", default="google_search")
    p_add.add_argument("--allow-email", action="store_true")
    p_imp = sub.add_parser("import", parents=[common])
    p_imp.add_argument("input")
    p_imp.add_argument("--source", default="google_search")
    p_imp.add_argument("--allow-email", action="store_true")
    sub.add_parser("dedupe", parents=[common])
    p_mark = sub.add_parser("mark", parents=[common])
    p_mark.add_argument("prospect_id")
    p_mark.add_argument("status")
    sub.add_parser("stats", parents=[common])
    sub.add_parser("contactable", parents=[common])
    return parser


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
        if not path.exists():
            write_csv(path, PROSPECT_COLUMNS, [])
        print("Ready: %s" % path)
        return 0
    if not path.exists():
        print("No prospect file at %s. Run: python3 tools/prospects.py init <role>" % path)
        return 1
    rows = read_csv(path)
    if args.command == "import":
        return do_import(args, path, rows)
    if args.command == "mark":
        return do_mark(args, path, rows)
    if args.command == "stats":
        print(stats_text(rows))
        return 0
    if args.command == "contactable":
        for row in rows:
            if is_contactable(row):
                print("%s  %s  %s" % (row["prospect_id"], row["name"], row["public_url"]))
        return 0
    if args.command == "dedupe":
        kept, _, skipped = merge_rows([], rows)
        write_csv(path, PROSPECT_COLUMNS, kept)
        print("Removed %d duplicates, %d prospects left." % (skipped, len(kept)))
        return 0
    row, reason = make_row(args.role or path.parent.name, {
        "name": args.name, "public_url": args.url, "headline": args.headline, "location": args.location,
        "fit_note": args.fit_note, "notes": args.notes}, args.source, args.allow_email)
    if not row:
        print("Not added: " + reason)
        return 1
    merged, added, _ = merge_rows(rows, [row])
    if not added:
        print("Already on the list (same public URL or same name and location).")
        return 0
    merged[-1]["prospect_id"] = next_ids(rows, 1)[0]
    write_csv(path, PROSPECT_COLUMNS, merged)
    print("Added %s (%s)." % (merged[-1]["prospect_id"], row["name"] or row["public_url"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
