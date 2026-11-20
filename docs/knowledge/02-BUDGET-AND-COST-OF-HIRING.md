# 02. Budget and the real cost of hiring

**Purpose.** Hiring costs more than the salary, and the cost of finding the person is only part of it.
Claude uses this doc to work out what a hire really costs, which path fits the budget, and what each budget level can honestly buy.

## Three costs, three questions

1. **Fully loaded cost of the person per year.** What does one employee cost to keep, in total?
2. **Cost per hire.** What does it cost to find, assess and start them, one time?
3. **Cost of getting it wrong or waiting.** What does an empty seat or a wrong hire cost the business?

Do not mix them. A cheap search can lead to an expensive wrong hire. An expensive search can still be right for a key role.

## Fully loaded cost (yearly)

```
loaded_yearly_cost = base_pay
                   + employer_costs           (base_pay x employer_cost_pct)
                   + equipment_and_software   (laptop, licences, desk, phone)
                   + management_time          (manager hours per week x 52 x manager hourly value)
                   + training_and_tools
```

`employer_cost_pct` is the extra the employer pays on top of pay (taxes, insurance, benefits, paid leave).
It differs a lot by country and by contract type. **Starting assumption, replace with your own data:** 25 percent.
Ask your accountant or payroll provider for the real figure. For a contractor or freelancer it is usually near zero on the pay line, but you may pay a higher day rate.

**Example (made up).** Northlight Home Services plans one scheduling coordinator. Base pay 36,000 (currency units of your choice), employer costs 25 percent = 9,000,
so the tool shows a loaded cost of 45,000 a year, not 36,000. Add equipment and software 1,500 and manager time
2 hours a week x 52 x 25 = 2,600 by hand and it is about 49,100. The tool adds only base pay and the employer cost percent.

## Every part of cost per hire

| Part | What it is | Who pays | Usually |
| --- | --- | --- | --- |
| Advertising | Paid job boards, boosted posts | Cash | Optional |
| Sourcing tools | Paid seats on a board, outreach or form tools | Cash | Optional |
| Recruiter or agency fee | A share of first year pay, or a flat fee | Cash | Only on that path |
| Team time | Hours of owner, manager and interviewers x their hourly value | Time | Always, often the largest |
| Candidate tests | Paid work samples (pay candidates fairly for real work) | Cash | Sometimes |
| Verification | References, right to work checks, background checks where lawful | Cash | Sometimes |
| Sign on, relocation | One time extras | Cash | Rare |
| Onboarding | Setup, training, buddy time | Time | Always |
| Ramp | The months the person is paid but not yet fully productive | Time | Always |
| Vacancy | What the empty seat costs while you search | Opportunity | Depends |

Formula:

```
cost_per_hire = advertising + tools + recruiter_fee + verification + candidate_tests + sign_on
              + (hours_per_hire x hourly_value) + onboarding_cost
```

`tools/budget_planner.py` takes these as options (`--board-spend`, `--tool-spend`, `--recruiter-fee-pct`, `--hours-per-hire`, `--hourly-value`).
Your own time is not free. If you earn or are worth 40 an hour and spend 30 hours on one hire, that is 1,200 of cost even if you pay nobody.

## The five paths

| Path | What it means | Cash cost | Your time | Best when |
| --- | --- | --- | --- | --- |
| 1. Do it yourself with this system | Claude plans, writes, screens, drafts messages. You post, send, interview, decide. | Near zero | Medium | Small budget, you can spare a few hours a week |
| 2. Job boards plus this system | Same as 1, plus paid posts or board seats to widen reach | Small to medium | Medium | Roles where candidates look on boards, you need volume |
| 3. Agency or recruiter | They source and often pre screen. You still interview and decide. | Fee, often a percentage of first year pay | Low to medium | Senior or hard to find roles, little time, budget available |
| 4. Contractor or freelancer | Pay for hours or a project, no employment | Higher rate, no long term cost | Low | Short, clear, or uncertain work (doc 04) |
| 5. AI plus a part time person | Automate the repeatable part, hire part time for the human part | Tool cost plus part time pay | Medium to set up | The role is mostly routine with a human judgment core (doc 04) |

Fee path math (`--recruiter-fee-pct` in the planner). **Starting assumption, replace with the quote you get:** 20 percent of first year base pay.
With base pay 36,000 that is 7,200 per hire. Always ask for the real terms: when is the fee due, what if the person leaves early, is there a replacement guarantee.

## What each budget tier realistically buys

Tiers compare the cash you can spend per hire with ONE MONTH of base pay, so they work in any currency and for
any pay level. One month is about 8.3 percent of first year pay. **Starting assumptions, replace with your own data.**
The tool prints the tier it picks.

| Tier | Cash per hire, as a share of one month of base pay | What it buys | What it does not buy |
| --- | --- | --- | --- |
| None | under 0.05 | Path 1 only: free posting places, referrals, your own audience, Google search of public pages, this system | Speed, paid reach, agency search |
| Small | 0.05 to under 0.25 | Path 1 plus one or two paid job posts, a paid test for finalists | Search firms, many paid boards at once |
| Medium | 0.25 to under 1.0 | Path 2 with several paid posts, a board seat for a month, outreach tools, paid work samples | A full agency search on a senior role |
| Large | 1.0 or more | Path 3 for the hard part (shortlist) while you still run interviews, or several paid channels at once | A guarantee of the right person |

Reading it: more cash buys speed and reach, never judgment. Judgment (the scorecard, the interview, the decision) is always yours, with Claude's help.

## Do this

1. Ask for the base pay range first (doc 05 helps you find it). Everything else is a ratio of it.
2. Run `python3 tools/budget_planner.py --base-pay 36000 --hires 1` (put your numbers in). Read the loaded yearly cost and the cost per hire by path.
3. Add your own time. Pass `--hours-per-hire` and `--hourly-value`, otherwise the plan looks cheaper than it is.
4. Pick the path from the table: lowest cash that still meets your timeline. If the timeline is short and the cash is tiny, say so and pick the least bad option.
5. Set a hard budget cap per hire (`--budget`) and a stop rule: if there are fewer than X good finalists by week Y, widen sourcing before you spend more.
6. For several identical hires, price the batch, not one hire times N (doc 03). Fixed costs (ads, tools) are shared.
7. Compare paths on cost of getting it wrong too: a senior hire that fails costs far more than the fee. Spend more on the roles where a mistake hurts most.
8. Write the decision in `hiring/<role>/plan.md` with the numbers, so the next hire starts from facts.

## Common mistakes

- Comparing a salary to a fee and forgetting employer costs, equipment and management time.
- Treating your own hours as free.
- Paying for reach before the post and the scorecard are good. Paid reach amplifies a weak post.
- Choosing an agency for a role with many easy applicants (you pay for what boards give you).
- Choosing "free" for a role that is urgent and senior. Time is the real price.
- Cutting the budget for onboarding. Ramp is the biggest hidden cost of a new hire.
- Using a contractor for a long, central role (it often costs more over a year and leaves a gap when they go). See doc 04.
- Not asking recruiters about guarantees and fee triggers in writing.

## Numbers

All starting assumptions live in one place: the assumptions printed by `tools/budget_planner.py`. Replace them with your data.

| Assumption | Starting value | Where to get the real one |
| --- | --- | --- |
| Employer cost percent | 25 percent | Accountant or payroll provider |
| Recruiter fee percent | 20 percent of first year base pay | The actual quote |
| Hours of your time per hire | 25 hours | Count yours after the first hire |
| Hourly value of your time | 30 in the tool, use your own | Owner pay or the pay of the people involved |
| Contractor premium on the hourly rate | 30 percent over the employee hourly rate | A real quote |
| Contractor hours per year (to compare rates) | 1,800 | Your own plan |
| Share of your time the recruiter path still needs | 0.25 of the hours | Your own history |
| AI tools cost, path 5 | 3 percent of base pay | Your real tool bills |
| Part timer covers | 50 percent of the hours | Your own plan |

**Worked example (made up).** `python3 tools/budget_planner.py --base-pay 36000 --hires 1 --hourly-value 40 --board-spend 600`
prints a loaded cost of 45,000 and these costs to find and hire one person: path 1 (you plus this system) 1,000,
which is 25 hours x 40. Path 2 (adds the 600 board spend) 1,600. Path 3 (recruiter) 7,450, which is the 20 percent fee of
7,200 plus a quarter of your 25 hours. Path 4 (contractor) 400 in hiring effort, and you compare it by the hourly rate
it prints, not by that number. Path 5 (AI plus a part timer) 1,680.
These numbers show how to calculate. They are not benchmarks. Use the tool with your own figures.

**Cost of a vacancy (rough):** weekly value the role creates (or protects) x weeks empty. Only use a number you can defend.

## Ask the owner

1. What is the base pay range you can afford? (Default: use the market range we find together, doc 05.)
2. How much cash can you spend on finding this person, in total? (Default: none, start with path 1.)
3. How many hours a week can you give to hiring? (Default: 4.)
4. What is the yearly employer cost on top of pay in your country or contract type? (Default: 25 percent, check with your accountant.)
5. Is the role urgent and senior enough to justify a recruiter? (Default: no, try path 2 first for 3 weeks.)
