# 03. How many people to hire, and how to time it

**Purpose.** The number of people, and the way you stage their start, changes the whole plan.
Claude uses this doc to decide between one hire and a group, batch or rolling hiring, how many offers to make, and how to protect the team while new people ramp up.

## First: is the number right?

Before planning the funnel, check the number itself. Count the work, not the feelings.

1. List the outcomes the role must deliver per month (doc 05).
2. Estimate the workload per person: how much of that outcome one fully ramped person can handle. Use your own history, not a guess from the internet.
3. Divide: `people_needed = total_workload / workload_per_person`, then round up only if the extra part is real work, not hope.
4. Check the budget: `people_needed x loaded_yearly_cost` (doc 02) must fit, or the plan must change.
5. Check the alternatives: part of the load may be automated or covered by a contractor (doc 04).

**Example (made up).** Northlight takes 120 booking requests a week. One scheduling coordinator can handle about 60 a week (starting assumption, check by timing real work).
120 / 60 = 2 people. But a tool now handles the simple half, so the real need is 1 coordinator plus the tool. Test that before hiring two.

## One hire or several identical hires

| Question | One hire | Several identical hires (same role, same scorecard) |
| --- | --- | --- |
| Scorecard | One, written carefully | One, shared. Same bar for everyone |
| Sourcing | Targeted, deep | Wider, more volume, repeat the same channels |
| Interviews | One loop per finalist | One standard loop, scheduled in blocks |
| Offers | One offer, a backup ready | Several offers, plus a backup list |
| Cost per hire | Highest per person | Lower per person, fixed costs are shared (ads, tools, form setup) |
| Risk | One bad hire is one problem | Same flaw repeated if the scorecard is wrong. Pilot first |
| Onboarding | One to one | Group sessions plus one buddy each |

Rule of thumb: if the number of hires is 3 or more, treat it as a batch project with a plan, a calendar and a daily pipeline check.
For 10 of the same role, hire a first small wave (2 to 3), learn from them, then run the rest. This is a planning rule, not a law.

## Batch or rolling

| | Batch hiring | Rolling hiring |
| --- | --- | --- |
| How | One window: post, screen, interview, offer, all start together | Always open, hire as good people appear |
| Good for | Seasonal staff, a launch, a class of trainees, many same roles | Steady growth, hard to find roles, one or two seats a quarter |
| Pros | Efficient, one onboarding, fair comparison of candidates side by side | No deadline pressure to settle, builds a talent list |
| Cons | Pressure to fill seats with whoever is there. Everyone starts at once | Slower, can feel endless, candidates wait without an answer |
| Needs | A fixed calendar, a closing date, enough interviewers | A standing post, a pipeline owner, a weekly review |

Mix is common: rolling for the core team, a batch when a busy season or new location needs a group.
Whatever you choose, give candidates dates: when the post closes, when they hear back.

## Offers: overhire to cover acceptance and no shows

Not everyone you offer will say yes, and not everyone who says yes will start. Plan for it without being unfair to candidates.

```
offers_needed = hires / offer_acceptance_rate      (round up)
```

**Starting assumption, replace with your own data:** acceptance 0.80. This is the number `tools/funnel_calculator.py` uses.
Example: 10 hires / 0.80 = 12.5, so plan for 13 offers. The tool does not model people who accept and then do not show up:
if that has happened to you, lower the acceptance rate in your own assumptions file (`--assumptions`) to cover it.

Two honest ways to use this:

1. **Sequential with a backup list (default, safest).** Make offers to the top candidates. As each declines, move to the next on the ranked list. No promise is ever withdrawn.
2. **Parallel overbooking (only if you would truly take everyone).** Make slightly more offers than seats only when you could afford to hire all of them if all accept. Never make an offer you intend to withdraw.

## Backup candidates (silver medalists)

People who were good but not chosen are your cheapest future hires.

- Keep a ranked backup list per role: finalists who passed the bar but lost to someone slightly stronger.
- Tell them honestly: "you were a strong finalist, can I keep your details for the next opening?" Keep the data only with their yes (doc 12 for privacy).
- Keep the list in `hiring/<role>/` and mark them in the pipeline notes. Review it before you pay for new sourcing.
- Contact backups within a few days of a decline or no show. Do not leave them waiting for weeks.
- Re check fit: the role and the person can both change in a few months.

## Staggered starts

Starting everyone on the same day is easy to organise and hard to manage. Stagger when the team cannot absorb many newcomers at once.

1. **Cap newcomers per manager.** Starting assumption: a manager can properly support 2 to 3 new people at the same time. Test and adjust.
2. **Stagger by one to two weeks** for groups above that cap, so each person gets real attention in week one.
3. **Keep a group start for group training** if the training is the same for everyone (for example a short product course), then split into teams.
4. **Do not stagger so much that the early joiners leave before the last one arrives** (offer acceptance fades with long waits).

## Team balance

When you hire more than one person, think about the team, not only each person.

- **Skills coverage.** Do not hire three people with the same weakness. Check the scorecard against the current team's gaps (job related gaps only).
- **Seniority mix.** A team of only new people needs a strong lead. Add or name a more experienced person first.
- **Workload shape.** Peaks and valleys: hire part time or flexible hours if the work comes in waves.
- **Succession.** If one person leaves, who covers? Cross train at least two people on critical tasks.
- **Fairness.** Balance means job related coverage. It does not mean "someone like us". Never use age, gender, background or "culture fit" as balance criteria.

## Ramp: when does a new hire pay back?

`ramp_months` is the time from start until the person works at the expected level. Starting assumption: 3 months for an entry role, longer for senior or complex roles. Use the scorecard's 90 day outcomes to define "ramped".

```
ramp_cost = months_ramping x loaded_monthly_cost x (1 - average_productivity_during_ramp)
```

If average productivity during ramp is about half (starting assumption), a 3 month ramp costs about 1.5 months of loaded pay in lost output. Plan it into the budget (doc 02).
For a batch, ramp costs multiply, so plan extra manager time and check outputs weekly.

## Do this

1. Verify the number with workload math. Challenge any plan that says "we need 5" without a calculation.
2. Run `python3 tools/funnel_calculator.py --hires N` for N hires. It handles batch hiring: overhire offers for acceptance rate and a backup list.
3. Choose batch or rolling and write the dates (post closes, interviews, offers, start dates) into `hiring/<role>/plan.md`.
4. For 3 or more identical hires, pilot a first wave and review before the rest.
5. Build the ranked backup list as you interview. Do not wait until the end.
6. Plan manager capacity and stagger starts if needed. Name a buddy for every newcomer.
7. Plan the first 30 60 90 days (doc 11 and `templates/interviews/onboarding-30-60-90.md`).
8. Review after the first month: did you hire the right number? Adjust before the next wave.

## Common mistakes

- Hiring for the peak week and paying all year.
- Hiring several people with the same untested scorecard, then repeating the mistake several times.
- Filling a batch to the number by lowering the bar. An empty seat is cheaper than a bad hire.
- Making more offers than you can honour, then withdrawing some.
- Starting everyone on one day with no buddy and one overloaded manager.
- Letting the backup list go cold.
- Ignoring ramp, then judging the new people at week two.
- Treating "team balance" as "people like us".

## Numbers

| Assumption | Starting value | Replace with |
| --- | --- | --- |
| Offer acceptance rate | 0.80 | Your last 10 offers |
| Show up rate after accepting | 0.95 | Your own history |
| Newcomers one manager can support at once | 2 to 3 | Your manager's own view |
| Ramp, entry role | 3 months | The 90 day outcomes in the scorecard |
| Productivity during ramp | about 50 percent | A short manager estimate at week 4 and week 8 |

All of these are starting assumptions. They are not statistics. The funnel tool prints its own assumptions and lets you replace them from a file (`--assumptions`).

## Ask the owner

1. How many people do you think you need, and what is that based on? (Default: one, and we check the workload math.)
2. Is this a one time group or an ongoing need? (Default: ongoing, rolling hiring.)
3. By what date must the first and the last person start? (Default: first in 8 weeks, no hard last date.)
4. How many new people can one manager support at the same time? (Default: 2.)
5. May we keep strong finalists on a backup list, with their permission? (Default: yes, with consent.)
