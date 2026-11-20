---
name: hiring-source
description: Finds prospects (people who could be right for the role but have not applied) across the public web and the user's own board searches, then keeps a clean prospects list. Use when the user says find candidates, sourcing, prospects, headhunt, find people for this role, or when applicants are too few.
---

# Hiring source: find prospects

Read `docs/knowledge/06-SOURCING-PLAYBOOK.md` and `docs/BROWSER-RULES.md`. Prospects come from three lanes. Be honest with the owner about which lane Claude runs.

## Lane 1: public web search (Claude runs this)

1. `python3 tools/make_search_strings.py hiring/<role>/scorecard.json --location "<city or remote>"` gives the strings.
2. Run the Google style strings with your web search tool. Use only what appears in public search results and public pages the person published (portfolios, personal sites, GitHub profiles, conference speaker pages, public project pages, published articles). Do NOT open or scrape LinkedIn, Indeed, Naukri or any job board page, do not guess or harvest email addresses.
3. For each good match keep only: name, a work related headline, location, the public URL and one line on why they fit the scorecard (a fact from the page, never invented). Add them with `python3 tools/prospects.py add ...` or import a list. Run `python3 tools/prospects.py dedupe`.

## Lane 2: the user's own board searches (the user runs, Claude helps)

LinkedIn, Indeed, Naukri and similar sites do not allow bots and scrapers, so the owner runs the searches in their own account. Give the owner the exact strings from `make_search_strings.py` with 3 plain steps (open search, paste, apply these filters). Ask them to export results or paste profile URLs and headlines into `hiring/<role>/inbox/`. Then you read the pasted file, score the fit with the scorecard, and import with `prospects.py import`. If the owner has a recruiter product with its own export, use that export.

## Lane 3: people the owner already knows

Ask for 5 names from past colleagues, customers, a community or an old employer, and for 3 people who would know good candidates. Write the referral ask from `templates/messages/06-referral-ask.md`.

## Rank

Rank prospects by fit to the scorecard (Claude's reading of the public facts, label it a first look, not a score). Show the top 10 in a small table with the reason and the public link. Offer: "Shall I write messages for these?" (then `hiring-outreach`).

## Rules

Minimal data only (no private details, no family, no photos). Respect `opt_out` and `stopped`. Say plainly how many came from each lane. Never promise "I found 500 people": say what is real. If lane 1 finds few, say that the best channel for this role is probably lane 2 or referrals and explain.
