# AI Hiring System

**Open this folder in Claude Code and it runs your hiring: research, plan, scorecard, job posts, prospects, scoring, outreach, interviews.**

<!-- counts: skills=11 commands=8 scorecards=12 messages=20 knowledge=14 candidates=60 -->

This is a free folder of instructions, tools, templates and fake practice data. You open it in Claude Code and Claude
works as your hiring expert: it learns about your company, plans the hire, and prepares every step. You stay in charge:
Claude drafts, you decide, you press Post and Send, and a person makes every no and every offer.
It is for any business owner or manager who hires, not only tech companies.

## Start here

1. **Install Claude Code** and make sure `python3 --version` shows 3.9 or newer. Docs: https://code.claude.com/docs
2. **Open this folder** in Claude Code.
3. **Paste the prompt** from [02-QUICK-START-PROMPT.md](02-QUICK-START-PROMPT.md), or type `/hire-start`.
4. **Answer the browser question**, then give your company name, your website and one more page about you.

Want to see it work first? `python3 examples/01_full_demo.py` runs the whole funnel on a made up company in about
a second, offline, with no key. More in [00-START-HERE.md](00-START-HERE.md) and [01-SETUP.md](01-SETUP.md).

## What is inside

| What | How many | Where |
| --- | --- | --- |
| Skills (what Claude knows how to do) | 11 | `.claude/skills/` |
| Commands (`/hire-start`, `/hire-plan`, and 6 more) | 8 | `.claude/commands/` |
| Role scorecards (SDR, bookkeeper, engineer, designer, and 8 more) | 12 | `templates/scorecards/` |
| Message templates (outreach, invites, declines, offers) | 20 | `templates/messages/` |
| Job post formats, application form, interview kit templates | 6 post formats, 1 JSON-LD, 1 form with screening questions, 6 interview files | `templates/` |
| Knowledge docs (the hiring brain) | 14 | `docs/knowledge/` |
| Sample candidates (fake, across 3 roles) | 60 | `data/sample/` |
| Tools (Python, standard library only) | 24 files, 20 run from the command line | `tools/` |
| Tests | 11 test files, 222 tests | `tests/` |
| Runnable offline examples | 5 | `examples/` |

## What makes it smart

- **A short, staged start.** Claude asks one question first (your browser), researches your company from the public web, tells you what it understood, and suggests at most 4 real moves tied to money, speed or risk. It does not hand you a long form.
- **Budget, quantity, timeline and funnel math.** `tools/budget_planner.py` and `tools/funnel_calculator.py` work out the real cost of a hire, how many offers to make for several identical hires, and how many people you need at each stage. Every assumption is printed so you can replace it with your own.
- **Blind scoring with evidence.** Names, contact details and gendered words are removed before scoring. Every score comes with a quote from the text. Wording that tries to give orders to an AI is flagged and sent to a person.
- **A weekly leak review.** `tools/pipeline.py weekly` shows where people stall and what to change. After a few hires it uses your own conversion rates instead of the starting assumptions.

## Optional: Jev

Jev is a fast scoring model from TypeSafe AI. This kit can use it to score big batches quickly, but it is not needed:
Claude can score on its own, and Claude offers Jev once and moves on if you say no. A practice mode with a FAKE Jev runs
offline with no key. Setup, cost and privacy notes: [docs/JEV-OPTIONAL.md](docs/JEV-OPTIONAL.md). This kit is independent
and not made or endorsed by TypeSafe AI.

## Honest limits

- Claude never drives LinkedIn, Indeed, Naukri or other job boards. Their rules do not allow bots. You run those searches in your own account and paste or export the results. Claude writes the search strings, posts and messages.
- You press Post and Send. Nothing is posted, sent, created or rejected without your clear yes. A person decides every no and every offer.
- The sample company and the 60 candidates are made up. Results on them say little about your applicants: see [docs/SAMPLE-RESULTS.md](docs/SAMPLE-RESULTS.md) for what the offline baselines got right and wrong. The real Jev and live Claude scoring were not measured there.
- Numbers in the tools are starting assumptions, not benchmarks. Law and platform rules change: [docs/knowledge/12-LAW-FAIRNESS-AND-PRIVACY.md](docs/knowledge/12-LAW-FAIRNESS-AND-PRIVACY.md) is an overview, not legal advice.
- Independent project. Not made or endorsed by TypeSafe AI or Anthropic.

## More

[docs/HOW-IT-WORKS.md](docs/HOW-IT-WORKS.md) · [docs/HONEST-LIMITS.md](docs/HONEST-LIMITS.md) · [docs/SECURITY-AND-DATA.md](docs/SECURITY-AND-DATA.md) · [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) · [docs/GLOSSARY.md](docs/GLOSSARY.md) · [CHANGELOG.md](CHANGELOG.md)

Run the tests: `python3 -m unittest discover -s tests`. MIT licence. Repo: https://github.com/onittindwani-ai/ai-hiring-system
