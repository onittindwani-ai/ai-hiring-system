---
name: hiring-pipeline
description: Tracks every person through the funnel, shows where it leaks, recalibrates the plan from real numbers, and writes the weekly review. Use when the user says status, where are we, weekly review, pipeline, what is stuck, or at the end of any hiring step.
---

# Hiring pipeline and weekly review

## Keep it current

After every step, update `hiring/<role>/pipeline.csv`: `python3 tools/pipeline.py add ...` and `python3 tools/pipeline.py move --role <role> <candidate_id> <stage>` (a move to rejected needs `--confirmed`, and only after the owner said yes). Stages: sourced, applied, screened, shortlisted, contacted, replied, interview_scheduled, interviewed, work_sample, reference_check, offer, accepted, hired, declined, rejected, withdrawn.

## Weekly review (run it every week, or when asked)

1. `python3 tools/pipeline.py stats --role <role>` and `python3 tools/pipeline.py weekly --role <role> --out hiring/<role>/WEEKLY.md`.
2. Re run `python3 tools/funnel_calculator.py --hires N --actual hiring/<role>/pipeline.csv`: the plan now uses real conversion rates, not the starting assumptions. Say whether the hire date still holds.
3. Find the leak: the stage with the weakest conversion or the oldest waiting items. Use `docs/knowledge/01-THE-HIRING-FUNNEL.md` for the cause and the fix (for example few applicants means change channels, many applicants and few shortlisted means the post is too broad, many offers declined means pay or speed).
4. Reply in 8 lines: where we are, the one leak, the one change to try, and the next safe step. Use a small table, not a wall of text.

## Next action rule

Every person in the pipeline has exactly one next action and a due date. Anyone waiting more than 7 days gets flagged. Candidates should never wait more than a few days for an answer: draft the message for the owner's approval.

## Close out

When the role is filled: thank and decline the rest kindly, keep silver medalists warm (`templates/messages/20-keep-warm-silver-medalist.md`), write 5 lines of lessons into `hiring/<role>/plan.md` and say what the next hire should do differently.
