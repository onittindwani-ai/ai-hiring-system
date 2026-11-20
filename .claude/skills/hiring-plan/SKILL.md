---
name: hiring-plan
description: Plans one hire or many hires end to end: the role, quantity, budget, timeline, hire versus automate, the funnel math, channel mix and a first week plan. Use after hiring-start, when the user names a role, or asks how many people to hire, what it will cost, or how long it will take.
---

# Hiring plan

Read first: `docs/knowledge/01-THE-HIRING-FUNNEL.md`, `02-BUDGET-AND-COST-OF-HIRING.md`, `03-HOW-MANY-TO-HIRE.md`, `04-HIRE-OR-AUTOMATE.md`, `05-DEFINING-THE-ROLE.md` (skim the parts you need, do not quote them at the user).

## Collect, with defaults (ask only what research and earlier answers do not give)

Open question first: "Who do you want to hire?" Then fill these yourself and show them in one small block for a quick yes:

| Item | Default if the user does not know |
| --- | --- |
| Role and level | from their words, nearest template in `templates/scorecards/` |
| How many of the same role | 1 |
| Budget for hiring (ads, boards, recruiter, tools) | "no paid budget, free posts only" |
| Pay range | found online for that role, region and level, with the source and date; never invented |
| Start by | 8 weeks from today |
| Remote or on site, where | from the company summary |
| Urgency (someone leaving, growth, new project) | normal |

Ask only the 3 to 6 items you could not fill, each with your proposed answer ("I assume 2 hires, ok?").

## Decide

1. **Hire or automate** (`04-HIRE-OR-AUTOMATE.md`): say in 3 lines which part of the job AI or a tool could do (the scorecard has an `automation_note`) and whether one person, a part timer, a contractor or an AI first plan fits better. If automation wins, say so honestly even though it means no hire.
2. **Quantity** (`03-HOW-MANY-TO-HIRE.md`): one person, a batch or rolling hiring. For several identical hires use one post, one scorecard, offers above the headcount for the acceptance rate, and a backup list.
3. **Money**: run `python3 tools/budget_planner.py ...` with the numbers you have. Show the fully loaded yearly cost, cost per hire by path, and whether the budget covers the plan. State every assumption.
4. **Funnel**: run `python3 tools/funnel_calculator.py --hires N ...`. Show how many prospects to contact, applicants to expect, screens, interviews and offers. Say clearly these are starting assumptions that the pipeline replaces with real numbers after the first batch.
5. **Channel mix by budget tier** (`06-SOURCING-PLAYBOOK.md`): say which channels, who runs each (Claude or the user), and the first week plan.

## Output

Create the role folder: `python3 tools/new_role.py <role-slug> --scorecard templates/scorecards/<match>.json`. Write `hiring/<role-slug>/plan.md` (one page: role, quantity, budget, timeline, hire or automate verdict, funnel numbers, channels, first week). Reply with the 8 line version and the single next step: "Shall I write the scorecard?" (then `hiring-scorecard`).

## Rules

Numbers are formulas or labelled assumptions, never invented market data. Pay ranges cite a source and a date. If the budget cannot cover the plan, say so and offer the cheapest honest path. Do not push a paid recruiter or a board: name the trade off. If a role looks like an illegal or unfair ask, say so politely and fix it (`12-LAW-FAIRNESS-AND-PRIVACY.md`).
