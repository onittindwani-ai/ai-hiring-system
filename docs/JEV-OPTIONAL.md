# Jev (optional): faster, steadier scoring

You do not need Jev. Claude scores candidates against your scorecard without it. Jev is a speed and steadiness upgrade for bigger batches.

## What Jev is

Jev is a model from TypeSafe AI. It does not write text. You give it some text and typed questions (rate this from 0 to 4, yes or no, which option) and it answers with a probability and a confidence, in a fraction of a second, for a very small cost. Facts below were checked on 2026-11-20 on typesafe.ai and docs.typesafe.ai. Check again before you rely on them.

## Why it helps hiring

| With Claude only | With Jev added |
| --- | --- |
| Reads each candidate, writes the evidence, slower for 100 or more | Scores every candidate on every criterion in about a second each |
| Judgement can drift across a long batch | Same questions every time, with a confidence number per answer |
| Costs your Claude usage | Costs cents for hundreds of candidates (see below) |

Claude still explains the top candidates, because Jev returns scores, not quotes. A person still decides.

## What it costs (verify)

- Price on typesafe.ai on 2026-11-20: 42 dollars per billion input tokens (about 4 cents per million). The output price was not stated on the pages we read.
- A real account on 2026-10-23 could not create an API key until credit was added (5 dollars worked). Expect to add a few dollars. Rules can change.
- Rough size (an estimate, not a measurement): one candidate with 8 criteria is a few thousand tokens, so a hundred candidates should be a fraction of a dollar. Run `python3 tools/jev_check.py` and the scoring run, both print the token cost.

## Setup in 6 steps

1. Go to https://typesafe.ai, create an account, accept the terms, open the console.
2. Add a few dollars of credit in Billing.
3. Create an API key at https://console.typesafe.ai/keys.
4. In your own terminal (not in the chat): `export TYPESAFE_API_KEY="your-key"`, or copy `.env.example` to `.env` and paste the key there.
5. Optional: install the TypeSafe skill. Claude Code: `claude plugin marketplace add typesafe-ai/skills` then `claude plugin install typesafe@typesafe-ai`. Other agents: `npx skills add typesafe-ai/skills --skill typesafe-ai`. Use only one method.
6. Test: `python3 tools/jev_check.py`.

## Privacy

TypeSafe's privacy policy (updated 2025-11-19) says it will not train models on your input and that the service is hosted in the United States. Candidate text is personal data. This system sends redacted text only (no names, emails, phones or links), and you should tell candidates that AI helps with screening. See `docs/knowledge/12-LAW-FAIRNESS-AND-PRIVACY.md`.

## Known weak spots (from TypeSafe's own docs)

Hidden instructions in the text, the order of answer options, and negations. That is why resumes are checked for injected instructions, why levels are asked as ordered scores, and why anything under 0.8 confidence goes to a person.

## If you say no

All good. Claude scores everything itself. You can switch on Jev any time by saying "set up Jev".

## Practice without a key

`python3 tools/score_candidates.py run --engine mock ...` starts a FAKE Jev (not the real model) on your own computer for the length of the run and scores through the same code the real engine uses, offline. To rehearse the real engine against the fake, run `python3 tools/mock_jev.py 8765` in one terminal and, in another, `TYPESAFE_API_KEY=practice JEV_BASE_URL=http://127.0.0.1:8765 python3 tools/score_candidates.py run --engine jev ...`.

This kit is independent and not made or endorsed by TypeSafe AI.
