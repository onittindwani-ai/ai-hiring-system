---
name: hiring-jev
description: Optional. Checks whether Jev (TypeSafe AI's fast decision model) is set up, offers it in a friendly way, installs it with the user's yes, explains any billing, and scores candidates with it. Not required: if the user declines, move on without pressure. Use when the user says Jev, faster scoring, TypeSafe, or when screening many candidates.
---

# Hiring Jev (optional)

Jev is a model from TypeSafe AI that does not chat. It answers typed questions (rate this, yes or no) with a probability and a confidence in about a second, for a very small cost. For hiring it is a fast, steady first pass over many candidates against the scorecard. Claude can always do the scoring without it. Facts and sources: `docs/JEV-OPTIONAL.md`. This is an independent kit, not made or endorsed by TypeSafe AI.

## 1. Check

Run `python3 tools/check_setup.py --jev`. It reports (never prints a key) whether `TYPESAFE_API_KEY` is set and whether the TypeSafe skill seems installed. Read `config/profile.json` field `jev`: `ready`, `later`, `declined` or unset.

## 2. Offer, in a friendly way (once)

Use words like these, short:

> One optional extra: Jev. It scores each candidate against your scorecard in about a second and tells me how sure it is, so big batches are faster and steadier. You don't need it, I can score everything myself. It needs a signup at typesafe.ai and a few dollars of credit (scoring hundreds of candidates costs cents). Want me to set it up now, later, or skip it?

- **Skip**: "All good, no problem, we'll do it with Claude." Save `"jev": "declined"`. Move on. You may say one line, once, later when scoring more than 25 candidates; after a second no, never again.
- **Later**: save `"jev": "later"` and remind once at the next batch of more than 25.
- **Now**: continue below.

## 3. Set up (with a yes for each action)

Tell the user the honest cost and steps: sign up at https://typesafe.ai (Google or email), accept the terms, open the console, add a few dollars of credit (on 2026-10-23 the console would not create an API key until credit was added, so expect to add some, check the current rule), then create a key at https://console.typesafe.ai/keys.

Install the TypeSafe skill after a yes: for Claude Code `claude plugin marketplace add typesafe-ai/skills` then `claude plugin install typesafe@typesafe-ai`; for other agents `npx skills add typesafe-ai/skills --skill typesafe-ai`. Use only one method. Start a new session if it asks.

**The key never goes in the chat.** The user runs in their own terminal: `export TYPESAFE_API_KEY="your-key"`, or copies `.env.example` to `.env` and pastes the key there. Then ask them to say "it's set". Check with `python3 tools/jev_check.py`. If it works, save `"jev": "ready"`.

Privacy, in one line: TypeSafe's privacy policy (2025-11-19) says input is not used to train models and the service is hosted in the United States, so candidate text goes to a US service. This system sends redacted text only (no names, emails, phones, links), and the owner should tell candidates that AI helps with screening (`docs/knowledge/12-LAW-FAIRNESS-AND-PRIVACY.md`).

## 4. Score with Jev

`python3 tools/score_candidates.py run --engine jev --scorecard hiring/<role>/scorecard.json --candidates hiring/<role>/candidates/candidates.jsonl --out hiring/<role>/scores.json --shortlist hiring/<role>/shortlist.csv`

Always: anything with confidence under 0.8 on a must have, any injection flag, and any unknown gate goes to a person. Jev has known weak spots (hidden instructions in the text, the order of options, negations): that is why resume text is redacted, checked for injection, and a person decides. After the run, Claude explains the top candidates with evidence quotes (Jev returns scores, not quotes). Say the run cost (`jev_check.py` and the run print token cost).

## Offline practice

`python3 tools/mock_jev.py 8765` starts a FAKE Jev for practice (not the real model). Set `JEV_BASE_URL=http://127.0.0.1:8765` and use any text as a key.

## Never

Ask for or print the key. Spend money, sign up or add credit on the user's behalf. Push the user after a no.
