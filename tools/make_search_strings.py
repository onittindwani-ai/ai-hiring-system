"""Search string maker: boolean searches for each sourcing channel, built from a scorecard.

Usage:
    python3 tools/make_search_strings.py templates/scorecards/sales-development-rep.json
    python3 tools/make_search_strings.py <scorecard> --location "Austin" --seniority-words senior,lead
    python3 tools/make_search_strings.py <scorecard> --location "Austin|Remote" --out hiring/<role>/search-strings.md

What it does:
    Reads a scorecard and prints a markdown page with ready to paste search strings for Google
    (public web search), LinkedIn, Indeed, GitHub, Wellfound, Naukri and community posts. Every
    block says WHO RUNS IT. Claude only runs the Google strings, through public web search. The
    LinkedIn, Indeed, Wellfound and Naukri strings are for YOU to paste into your own account.
    Terms come from the scorecard title and criteria keywords, widened with a small starting list
    of synonyms (edit it for your field). Strings are kept short, quoted safely, and never ask for
    private data such as email addresses. Length limits here are our own readability hints, not
    platform rules. Check each platform's help page for its real limits.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hlib import load_json  # noqa: E402

# Starting list: edit for your field. Keys are lower case.
SYNONYMS = {
    "sdr": ["sales development rep", "business development rep", "bdr"],
    "sales development rep": ["sdr", "business development representative", "bdr"],
    "bookkeeper": ["accounts assistant", "accounting clerk", "accounts payable specialist"],
    "backend engineer": ["backend developer", "server side developer", "software engineer"],
    "outbound": ["prospecting", "cold outreach", "cold calling"],
    "crm": ["salesforce", "hubspot", "pipedrive"],
    "reconciliation": ["bank reconciliation", "reconciling accounts"],
    "api": ["rest api", "web services"],
    "customer support": ["customer service", "support specialist"],
    "excel": ["spreadsheets", "google sheets"],
}
PLATFORM_HINTS = {"google": 250, "linkedin": 250, "indeed": 250, "github": 200, "naukri": 250}
EXCLUDE_TITLES = ["intern", "recruiter", "student"]
TECH_WORDS = {"python", "api", "backend", "frontend", "software", "engineer", "developer", "sql", "javascript", "code"}

WHAT_NOT_TO_DO = [
    "Never scrape, crawl or automate LinkedIn, Indeed, Naukri, Wellfound or any job board, and never let a tool log in for you.",
    "Do not run bulk automated searches or use browser extensions that click through profiles for you.",
    "Do not guess or buy private email addresses. Use the platform's own message feature or a public work contact.",
    "Do not search on or filter by age, gender, race, religion, nationality, family status, health, photos or names.",
    "Do not message anyone until the owner has said yes to the exact text. Add 'Reply STOP' to cold messages.",
]


def quote(term):
    """Quote a term safely for a boolean string: strip quotes and odd characters, wrap phrases."""
    cleaned = re.sub(r'["\u201c\u201d\\]', "", str(term)).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return '"%s"' % cleaned if " " in cleaned else cleaned


def unique(items):
    seen, out = set(), []
    for item in items:
        key = item.lower().strip()
        if key and key not in seen:
            seen.add(key)
            out.append(item.strip())
    return out


def expand(term):
    return unique([term] + SYNONYMS.get(term.lower(), []))


def or_group(terms, max_chars):
    """Join terms with OR inside parentheses, adding terms only while the string stays under max_chars."""
    parts = []
    for term in terms:
        candidate = " OR ".join(parts + [quote(term)])
        if parts and len(candidate) + 2 > max_chars:
            break
        parts.append(quote(term))
    return "(%s)" % " OR ".join(parts) if len(parts) > 1 else (parts[0] if parts else "")


def locations(text):
    return [p.strip() for p in (text or "").split("|") if p.strip()]


def location_clause(locs):
    real = [l for l in locs if l.lower() != "remote"]
    parts = ([quote(l) for l in real] + (["remote"] if len(real) != len(locs) else []))
    return "(%s)" % " OR ".join(parts) if len(parts) > 1 else (parts[0] if parts else "")


def build_terms(scorecard, seniority):
    title_terms = expand(scorecard["title"])
    if seniority:
        senior = ["%s %s" % (word, scorecard["title"]) for word in seniority]
        title_terms = unique(title_terms[:1] + senior + title_terms[1:])
    musts = [c for c in scorecard["criteria"] if c.get("type") == "must"]
    ordered = musts + [c for c in scorecard["criteria"] if c.get("type") != "must"]
    skill_terms = []
    for criterion in ordered:
        for keyword in criterion.get("keywords", [])[:3]:
            skill_terms += expand(keyword)
    return title_terms, unique(skill_terms)


def join_clauses(*clauses):
    return " ".join(c for c in clauses if c)


def build_strings(scorecard, location="", seniority=()):
    titles, skills = build_terms(scorecard, seniority)
    locs = locations(location)
    loc = location_clause(locs)
    t_google, s_google = or_group(titles, 130), or_group(skills, 100)
    strings = {
        "google_xray_linkedin": {
            "runner": "Claude (public web search, snippets only)",
            "string": join_clauses("site:linkedin.com/in", t_google, s_google, loc)},
        "google_xray_portfolio": {
            "runner": "Claude (public web search, snippets only)",
            "string": join_clauses(or_group(["portfolio", "about me", "my work"], 60), t_google, s_google, loc,
                                   "-site:linkedin.com -site:indeed.com")},
        "linkedin_search": {
            "runner": "YOU, in your own LinkedIn account (Claude never opens LinkedIn)",
            "string": join_clauses(or_group(titles, 140), "AND", or_group(skills, 100),
                                   "NOT (%s)" % " OR ".join(EXCLUDE_TITLES)),
            "filters": "Use LinkedIn's own location filter: %s" % (", ".join(locs) or "choose your city or remote")},
        "indeed_search": {
            "runner": "YOU, in your own Indeed employer account if it includes resume search; "
                      "otherwise just read the applicants to your job post",
            "string": join_clauses(or_group(titles, 140), "AND", or_group(skills, 100)),
            "filters": "Set the location in Indeed's own location box: %s" % (", ".join(locs) or "your city or remote")},
        "naukri_search": {
            "runner": "YOU, in your own Naukri recruiter account (if your plan supports boolean search, "
                      "else use the top 5 keywords in the keyword box)",
            "string": join_clauses(or_group(titles, 140), "AND", or_group(skills, 100)),
            "filters": "Set the location filter in Naukri: %s" % (", ".join(locs) or "your city")},
        "wellfound": {
            "runner": "YOU, in your own Wellfound account (it uses filters rather than boolean strings)",
            "string": "Role: %s. Skills to filter: %s" % (scorecard["title"], ", ".join(skills[:6])),
            "filters": "Location: %s" % (", ".join(locs) or "your city or remote")},
    }
    if any(w in TECH_WORDS for w in re.findall(r"[a-z]+", " ".join(titles + skills).lower())):
        gh_loc = ('location:%s' % quote(locs[0])) if locs and locs[0].lower() != "remote" else ""
        strings["github"] = {
            "runner": "YOU in GitHub's own search box, or Claude through public web search (never by scraping GitHub)",
            "string": join_clauses("type:user", gh_loc, "repos:>3", quote(skills[0]) if skills else ""),
            "filters": "GitHub search qualifiers can change. Check GitHub's own search help before relying on them."}
    return strings


def community_prompts(scorecard, location):
    title = scorecard["title"]
    where = ("in %s " % location.replace("|", " or ")) if location else ""
    return [
        "Ask in a community you already belong to (by hand): 'I am hiring a %s %s(real pay range here). "
        "Who do you know who has done %s? Intro only, no pressure.'" % (title, where, scorecard["mission"].rstrip(".").lower()),
        "Ask three people you trust: 'Who is the best %s you have worked with, and are they open to a call?'" % title,
        "Ask former colleagues and past clients for referrals. Say what the job pays and why it exists.",
    ]


def render(scorecard, strings, location):
    lines = ["# Search strings for %s" % scorecard["title"], "",
             "Built from the scorecard. Nothing here has been run yet.", "",
             "Who runs what: Claude runs only the Google strings (public web search). You run everything else, "
             "in your own account, and paste or export the results into `hiring/<role>/inbox/`.", ""]
    for name, info in strings.items():
        lines += ["## %s" % name, "", "Who runs it: %s" % info["runner"], "", "```", info["string"], "```", ""]
        if info.get("filters"):
            lines += [info["filters"], ""]
        hint = PLATFORM_HINTS.get(name.split("_")[0])
        if hint and len(info["string"]) > hint:
            lines += ["Note: this string is %d characters. Trim terms if the site rejects it." % len(info["string"]), ""]
    lines += ["## Community and referral asks (you send these by hand)", ""]
    lines += ["- " + p for p in community_prompts(scorecard, location)]
    lines += ["", "## What not to do", ""] + ["- " + w for w in WHAT_NOT_TO_DO]
    lines += ["", "Synonyms come from a short starting list in tools/make_search_strings.py. Edit it for your field."]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build boolean search strings from a scorecard")
    parser.add_argument("scorecard")
    parser.add_argument("--location", default="")
    parser.add_argument("--seniority-words", default="")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    path = Path(args.scorecard)
    if not path.exists():
        print("Scorecard not found: %s" % path)
        return 1
    try:
        scorecard = load_json(path)
        if not isinstance(scorecard, dict):
            raise ValueError("expected a JSON object")
        seniority = [w.strip() for w in args.seniority_words.split(",") if w.strip()]
        strings = build_strings(scorecard, args.location, seniority)
    except (ValueError, KeyError, TypeError) as exc:
        print("This does not look like a scorecard (%s). Run tools/validate_scorecard.py on it." % exc)
        return 1
    text = render(scorecard, strings, args.location)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")
        print("Wrote %s" % args.out)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
