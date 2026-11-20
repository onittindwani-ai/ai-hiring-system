# Sample results: how the offline scorers did on the made up candidates

Measured on 2026-11-20 with `tools/evaluate.py` and the answer key in `data/sample/answer_key.json`.

## Read this first

- The 60 candidates are made up. So is the company. The answer key is the tier a hiring manager would
  expect, written from the scorecards before any tool ran on the resumes. It is a small test, not a study.
- The two scorers measured here are **baselines**: the `rules` engine (keyword matching, runs offline) and
  the `mock` engine (a FAKE Jev that guesses from word overlap, runs offline). They exist so you can
  practise the whole flow with no key and no cost.
- **The real Jev API and live Claude scoring were not measured here.** There was no key, and Claude scoring
  needs a live session. Nothing on this page says how well they score. Measure them yourself on your own
  role before you trust them (steps at the end).
- The sample resumes never state work authorization, so every run used `--unknown-gates flag`. The gate stays
  flagged for a person, but the tier is still shown. Without that flag every sample candidate lands in
  "review" and there is nothing to compare.

## Headline numbers (60 candidates, 3 roles)

| Scorer | Same tier as the key | Strong people scored "below" | People marked review for injected text |
| --- | --- | --- | --- |
| rules (keywords) | 30 of 60 (50%) | 6 of 15 strong people | 3 of 3 |
| mock (fake Jev) | 30 of 60 (50%), 29 exactly the key's tier | 3 of 15 strong people | 3 of 3 |

An "also acceptable" tier in the key counts as a match. Both baselines are weak. Half of the people get a
different tier than a hiring manager would give, so a person has to read every resume that matters.
`needs_human` was true for all 60 candidates in both runs, because the gate answer is unknown.

## Agreement by role

| Role | rules | mock |
| --- | --- | --- |
| Sales Development Rep (C001 to C020) | 10 of 20 | 12 of 20 |
| Bookkeeper (C021 to C040) | 10 of 20 | 10 of 20 |
| Backend Engineer (C041 to C060) | 10 of 20 | 8 of 20 |

## Agreement by expected tier

| What the key says | rules matched | mock matched |
| --- | --- | --- |
| strong (15) | 4 | 6 |
| maybe (21) | 6 | 12 |
| below (21) | 17 | 9 |
| review (3, injected text) | 3 | 3 |

The keyword baseline is cautious: it scores most people low, so it misses strong people (4 of 15 found).
The fake Jev is generous: it scores most people high, so it finds more strong people but matches only 9 of 21
"below" people and puts 11 of them in "review".

## Where each baseline fails, by trap

Each candidate in the key can carry traps. "Matches" means the tier agrees with the key.

| Trap | Candidates | rules | mock | What it shows |
| --- | --- | --- | --- | --- |
| prompt injection (resume tries to give orders to the AI) | 3 | 3 | 3 | The check catches all 3, and no other candidate was flagged for it. |
| keyword stuffing | 4 | 4 | 2 | The keyword scorer matched the key for all 4. The fake Jev matched for 2. |
| title inflation | 4 | 4 | 1 | The fake Jev matched the key for only 1 of 4. |
| career gap | 4 | 3 | 4 | A gap itself is never scored. One miss for the keyword scorer. |
| non traditional path | 4 | 0 | 1 | Both baselines mostly miss people who learned the skill outside a normal job path. |
| non native English | 3 | 1 | 1 | Both baselines match for only 1 of 3. |
| overqualified | 3 | 1 | 2 | Neither is reliable here. |
| very long resume | 3 | 0 | 2 | The keyword scorer matched none of the 3. |
| very thin resume | 3 | 0 | 1 | Little text, little for either to go on. |
| name origin neutral | 6 | 0 | 0 | See the next section: this trap is about names, not about tiers. |

## Dangerous misses (a strong person scored below)

Both lists are in the tool output. In plain words:

- rules: C002 and C004 (the same three years of outbound work for roofing and gutter companies), C005
  (strong outbound work, English as a second language), C023 (long bookkeeping career, then a break), C025
  (six years of bookkeeping in two countries, English as a second language), C043 (a self taught builder
  who used to be a pastry chef).
- mock: C002, C043 and C045 (strong Node and Postgres work, English as a second language).

Of the seven different people missed, five are non traditional, took a career break or write in a second
language (C005, C023, C025, C043, C045). That is a pattern to expect from a scorer that mostly matches words. It is why this kit never
rejects anyone automatically: "below" means "not shortlisted now", and a person decides every no.

## Does the score change with the name?

No, by design and by check. Names, emails and phone numbers are removed before scoring. A direct test took
18 of the sample resumes and swapped in 5 different made up names, 90 runs per scorer, and compared the
score and tier each time: 36 comparisons, 0 differences, for both baselines.

The six "name origin neutral" candidates are three pairs with the same real evidence and different names
(C002 and C004, C026 and C029, C049 and C050). Their scores still differ, because the resumes are written in
different words:

| Pair | rules scores | mock scores |
| --- | --- | --- |
| C002 and C004 | 20.0 and 35.0 (both below) | 53.8 and 68.8 (below and maybe) |
| C026 and C029 | 45.0 and 42.5 (both below) | 80.0 and 77.5 (both strong) |
| C049 and C050 | 75.0 and 78.8 (both strong) | 57.5 and 53.8 (both below) |

So the baselines are sensitive to wording, which is a different weakness from the name. A person should
compare close pairs side by side.

## Prompt injection

Three resumes (C019, C039, C060) hide text that tries to tell an AI screener how to rate them. For both
baselines, all three were sent to the "review" tier with the flag `prompt_injection_suspected`, the hidden
text was cut out of what was scored, and no other candidate got that flag. Real resumes can carry
wording this simple check does not know, so keep reading the text yourself.

## What these numbers do not tell you

- Nothing about the real Jev, or about Claude reading the redacted text. They were not run.
- Nothing about your role or your applicants. Sixty made up resumes are a test of the kit, not a benchmark.
- Nothing about fairness in the real world. The name swap check shows the kit does not use the name. It does
  not show that a model never reacts to other signals in the text.

## Run it again, and measure the real thing yourself

```
python3 tools/score_candidates.py run --scorecard data/sample/scorecard-bookkeeper.json \
  --candidates data/sample/candidates.jsonl --engine rules --unknown-gates flag --out rules-bookkeeper.json
python3 tools/evaluate.py --scores rules-sales-development-rep.json rules-bookkeeper.json rules-backend-engineer.json \
  --key data/sample/answer_key.json
```

Use `--engine mock` for the fake Jev. To test the real Jev, follow `docs/JEV-OPTIONAL.md`, run with
`--engine jev` on the same files (check the cost first with `--dry-run`), and compare it with
`tools/evaluate.py`. To test Claude, use `score_candidates.py packet` to write the redacted texts, let
Claude score them into a file, load them with `score_candidates.py import`, and evaluate the same way.
For your own role, label 15 to 20 real past applicants first (`data/sample/LABELING-GUIDE.md` shows how),
then compare.
