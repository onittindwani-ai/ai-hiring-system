# Changelog

## 1.0.0 (2026-11-20)

First release.

- A folder you open in Claude Code that runs the hiring funnel: company research, hire plan with budget, quantity and timeline, scorecard, job posts and application form, prospect sourcing, candidate scoring with evidence, outreach drafts, interview kits, and a weekly pipeline review.
- 11 skills and 8 commands (`/hire-start`, `/hire-plan`, `/hire-source`, `/hire-post`, `/hire-screen`, `/hire-reach`, `/hire-interview`, `/hire-weekly`).
- A short, staged start: one question first, research before asking, at most 4 suggested moves.
- 14 knowledge docs, 12 role scorecards, 20 message templates, 6 job post formats plus a JSON-LD template, an application form and interview templates.
- 24 Python files in `tools/` (standard library only, Python 3.9 or newer): planning (budget, funnel), sourcing (search strings, prospect list), scoring (blind redaction, injection check, bias check, scorecard validator, rules engine), messages (render and check), pipeline tracking, an Apps Script form maker, a kit linter.
- Optional Jev scoring (TypeSafe AI) with a client, a cost estimate and a FAKE Jev for offline practice. Claude can score without it.
- Fake sample data: one company, 3 role scorecards, 60 candidates, a hand written answer key and a labeling guide.
- 5 offline examples and 222 tests. `docs/SAMPLE-RESULTS.md` reports how the offline baselines did on the sample data. The real Jev API and live Claude scoring were not measured.

Checked on 2026-11-20 against:

- Claude Code docs (code.claude.com) and the Claude in Chrome support page.
- The Jev API as described at docs.typesafe.ai (model name `jev-latest`, endpoint `/v1/systemone`) and the price shown on typesafe.ai that day. Prices and billing rules can change, check before relying on them.
- Python 3.9.6 and 3.14 on macOS for the tests. CI runs them on Ubuntu with Python 3.12.
- Law and platform notes in `docs/knowledge/12-LAW-FAIRNESS-AND-PRIVACY.md` carry their own check dates. Not legal advice.
