---
name: hiring-scorecard
description: Builds and validates the scorecard (the weighted, job related criteria every candidate is judged on) before any resume is read. Use after the plan, when the user says scorecard, criteria, what should I look for, or before screening.
---

# Hiring scorecard

The scorecard is written and approved BEFORE anyone is scored. That is what keeps hiring fair and consistent.

## Steps

1. Start from the nearest template in `templates/scorecards/` (12 roles) or from `hiring/<role>/scorecard.json`. Read `docs/knowledge/05-DEFINING-THE-ROLE.md` and `08-SCREENING-AND-SCORING.md` when unsure.
2. Tailor it with what you know about the company (`config/profile.json`) and the plan: outcomes for the first 90 days, 5 to 8 criteria, at least 3 must haves with a `min_level`, weights that sum to 100, 5 level descriptions per criterion, keywords, interview questions and a work sample.
3. Remove anything that is not job related. Never use age, gender, nationality, race, religion, family status, health, photo, name, accent, "culture fit", "native speaker" or "digital native", or a proxy for them. Gates (like the legal right to work) are yes or no questions, and deal breakers must carry a job related reason.
4. Validate: `python3 tools/validate_scorecard.py hiring/<role>/scorecard.json`. Fix every error. Read the warnings.
5. Show the owner a compact table: criterion, must or nice, weight, what good looks like (one line). Ask: "Approve, or change a weight?" One question only.
6. After approval write `"approved": true` and the date into the scorecard. Do not change an approved scorecard after candidates are scored; if it must change, say that earlier scores are stale and re-score.

## Quality bar

Each criterion can be judged from evidence in a resume, an application answer or a work sample. If it cannot, rewrite it. Weights show what matters for the 90 day outcomes, not what is easy to read. Prefer outcomes ("has run outbound sequences that booked meetings") over credentials ("degree").

## Output

An approved `hiring/<role>/scorecard.json` and a 6 line summary. Next step: `hiring-post` (job post and form) or `hiring-source` (prospects).
