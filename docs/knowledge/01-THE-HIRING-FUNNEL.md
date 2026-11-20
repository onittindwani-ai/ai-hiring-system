# 01. The hiring funnel

**Purpose.** This is the map of the whole hiring process, from "we need someone" to "they are doing the job well".
Claude uses it to know which stage a business is in, what to measure there, and where hiring usually breaks.

## The funnel in one picture

Every hire is a funnel. Many people enter at the top, a few reach the bottom, and one (or a few) start work.

| # | Stage | Purpose | Pipeline stage names (tools/pipeline.py) | Who decides |
| --- | --- | --- | --- | --- |
| 1 | Plan | Decide if, who, how many, budget, timeline | (before the pipeline) | Owner |
| 2 | Define the role | Outcomes, must haves, level, pay | (scorecard) | Owner, Claude drafts |
| 3 | Source | Get people to know the job exists | sourced | Owner runs boards, Claude writes strings and posts |
| 4 | Apply | Make it easy to apply with the right information | applied | Candidate |
| 5 | Screen | Sort fast against the scorecard, by evidence | screened, shortlisted | Claude scores, human decides |
| 6 | Reach out | Invite the best prospects and shortlisted people | contacted, replied | Owner sends |
| 7 | Interview | Same questions, same scoring, for everyone | interview_scheduled, interviewed | Hiring team |
| 8 | Test | A short, paid or fair work sample when the job needs it | work_sample | Hiring team |
| 9 | Check | References and basic verification | reference_check | Owner |
| 10 | Offer and close | Make the offer, handle questions, get a yes | offer, accepted | Owner |
| 11 | Start | Onboarding, first 30 60 90 days | hired | Manager |
| 12 | Learn | Review the funnel and the hire, improve next time | (weekly review) | Owner, Claude reports |

Terminal pipeline stages: accepted, hired, declined, rejected, withdrawn. Every "rejected" is a human decision.
Claude never rejects anyone on its own, and the scoring tools never write "rejected".

## Purpose of each stage, in plain words

1. **Plan.** Do not start sourcing until you know the budget, the start date and how many people you need (docs 02, 03, 04).
2. **Define the role.** A role is a list of outcomes, not a list of tasks (doc 05). A fuzzy role produces a fuzzy funnel.
3. **Source.** More of the right people seeing the job. Quality of the top decides everything below it (doc 06).
4. **Apply.** The easier the form, the more people apply, and the more noise too. Design the form to filter lawfully (doc 07).
5. **Screen.** Score each person against the same scorecard. Look for evidence of doing the thing, not for keywords.
6. **Reach out.** Fast, honest, personal with real facts only. Speed matters more than polish.
7. **Interview.** Structured: the same questions, a rating sheet, notes written straight after.
8. **Test.** Use only when it predicts the job and is short. Respect the candidate's time.
9. **Check.** Ask references specific questions about the outcomes in the scorecard.
10. **Offer and close.** Be clear on pay, start date and what the first 90 days look like. Close within days, not weeks.
11. **Start.** A good hire can still fail without a plan for week one.
12. **Learn.** Compare what you predicted with what happened (the Numbers section below shows how).

## Do this

1. Write the funnel on one page before sourcing: target hires, target start date, who decides at each stage.
2. Run `python3 tools/funnel_calculator.py --hires 1` (or your number) to see how many people you need at each stage. It prints its starting assumptions, so you can see and change them.
3. Name one owner per stage. A stage with no owner is where candidates wait and disappear.
4. Set a response time rule per stage (for example: reply to every applicant within 3 working days, feedback within 2 days after an interview). Starting assumption, set your own.
5. Track every person in `hiring/<role>/pipeline.csv` with `tools/pipeline.py`. One row per candidate, always with a next action and a due date.
6. Review the funnel every week with `python3 tools/pipeline.py weekly --role <role> --out hiring/<role>/WEEKLY.md`.
7. Keep one rule for fairness at every stage: same criteria for everyone, job related only, a human makes every "no".
8. After the hire starts, write down what you would change (stage 12). The next hire gets cheaper and faster.

## How a pipeline fails (read these patterns)

| Symptom | Likely stage | Usual cause | First fix |
| --- | --- | --- | --- |
| Almost no applicants | Source or Apply | Job not seen, pay missing, form too long | Post in more places, add pay range, cut the form |
| Hundreds of applicants, none good | Source or Define | Vague post, wrong channels | Sharper outcomes and must haves, better channels |
| Good applicants, few interviews | Screen or Reach out | Slow reply, no owner | Reply in 48 hours, assign an owner |
| Many interviews, no offers | Define or Interview | Role keeps changing, no scorecard | Freeze the scorecard, rate with the same sheet |
| Offers, few acceptances | Offer or Source | Pay below market, slow process, unclear job | Check pay, shorten the process, call the candidate |
| Hires leave in the first months | Define or Start | Job was not as described, no onboarding | Honest job post, 30 60 90 plan |
| Everything takes forever | Any | Too many steps, one busy decision maker | Remove steps, set decision dates |

## Common mistakes

- Starting at stage 3 (posting a job) before stages 1 and 2. The post then says nothing useful.
- Judging the funnel by the number of applicants instead of the number of good finalists.
- Letting the best candidates wait. Good people are usually in several processes.
- Adding steps "to be safe" (a 5th interview). Each step loses people. Add a step only if it tells you something new.
- Changing the role halfway and keeping the old candidates in the pool.
- Rejecting by silence. Send a short, kind close out message (a human sends it).
- Forgetting to count the hours your own team spends. They are a real cost (doc 02).
- Measuring only the top and bottom. The leak is almost always in one middle stage.

## Numbers

The funnel works backwards from the people you need. Formula (rates are fractions between 0 and 1):

```
offers_needed       = hires / offer_acceptance_rate
finalists_needed    = offers_needed / finalist_to_offer_rate
interviews_needed   = finalists_needed / interview_to_finalist_rate
shortlisted_needed  = interviews_needed / shortlist_to_interview_rate
screened_needed     = shortlisted_needed / screened_to_shortlist_rate
applicants_needed   = screened_needed / applicant_to_screened_rate
prospects_to_contact = (applicants you want from outreach) / prospect_reply_to_apply_rate
```

**Starting assumptions, replace with your own data.** The tool keeps these in one dictionary and prints them.
The numbers below are the ones `tools/funnel_calculator.py` prints. They are not market statistics.

| Rate | Starting value |
| --- | --- |
| offer acceptance | 0.80 |
| finalist to offer | 0.50 |
| interview to finalist | 0.40 |
| shortlist to interview | 0.70 |
| screened to shortlist | 0.50 |
| applicant to screened | 0.60 |
| prospect to applicant (only if you source) | 0.10 |

**Worked example (made up).** You need 1 hire.
offers = 1 / 0.80 = 1.25, round up to 2 offers (one may decline).
finalists = 2 / 0.50 = 4. interviews = 4 / 0.40 = 10. shortlisted = 10 / 0.70 = about 15.
screened = 15 / 0.50 = 30. applicants = 30 / 0.60 = 50. So with these assumptions you need about 50 applicants
to fill one role, or about 500 prospects contacted if nobody applies by themselves (50 / 0.10).
If you only get 20 applicants, the plan says to widen sourcing or accept a longer timeline, not to lower the bar.

**Use real data when you have it.** After 20 or more candidates have moved through, run
`python3 tools/funnel_calculator.py --hires 1 --actual hiring/<role>/pipeline.csv` to replace the assumptions with your own rates.
A small business may never reach large samples. That is fine: treat the rates as rough and update them after each hire.

**Time.** Estimate calendar time per stage, add them, and compare with your target start date. Starting assumption, replace with yours:
source and apply 1 to 3 weeks, screen 2 to 5 days, interviews 1 to 2 weeks, offer 3 to 7 days, notice period before start (varies by country and seniority).
The tool's own starting assumption is 4 weeks from first applicant to offer plus 2 weeks from offer to start, so about 6 weeks.
Work backwards from the date you need the person: `--weeks W` in the funnel tool checks if the plan fits.

## Ask the owner

1. When do you need the person to start? (Default: 8 weeks from today.)
2. Who makes the final yes or no, and who else is in the interviews? (Default: the owner decides, one other person helps.)
3. How fast can you reply to a good candidate? (Default: within 2 working days.)
4. Have you hired this role before? Do you have past numbers? (Default: no, use the starting assumptions.)
5. Do you want weekly funnel reviews, and on which day? (Default: yes, Monday.)
