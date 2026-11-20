# 04. Hire, automate, contract, outsource or upskill

**Purpose.** Not every need is a hire. This doc gives Claude a way to decide between a new employee, automation with AI or software,
a contractor, an agency or outsourced service, and training someone you already have. It also shows how to split one role into a machine part and a human part.

## The five options

| Option | What you get | You pay | Good for |
| --- | --- | --- | --- |
| Hire an employee | A person who learns your business and grows | Loaded cost every month, plus hiring cost | Ongoing, central, judgment heavy work |
| Automate with AI or software | Repeatable work done by a tool, with human review | Tool cost, setup time, review time | Routine, rule based, high volume work |
| Contractor or freelancer | Skilled hours or a finished project, no employment | Higher rate per hour, no long term cost | Short, clear, or uncertain work; rare skills |
| Agency or outsourced service | A whole function run by another firm | Retainer or per project fee | A function you do not want to build in house |
| Upskill someone you have | A current person takes on more | Training time, maybe a pay change | The person is willing and the work fits their path |

You can combine them. The best answer is often "automate 60 percent, hire a part time person for the other 40".

## The decision procedure (ask in this order)

Answer each question for the work you need done. Stop at the first strong signal, then check the others.

1. **Is the work ongoing or one time?** One time or a short project points to a contractor or agency. Ongoing points to an employee or automation.
2. **Is it routine and rule based, or does it need judgment, trust and relationships?** Routine points toward automation. Judgment and relationships point toward a person.
3. **How much volume?** Many repeats of the same task favour automation. Low volume favours a person or a contractor, because setup would cost more than the work.
4. **What happens when it goes wrong?** If an error is cheap and easy to catch, automation with review is fine. If an error is costly, harmful or hard to undo (money, health, safety, legal), a person must decide.
5. **Does the work touch private or sensitive data?** If yes, check privacy and contracts first (doc 12). Do not paste private data into a tool you have not checked.
6. **Can the task be written down clearly?** If you cannot describe the steps and what "good" looks like, automation will fail and so will a rushed hire. Write the scorecard first (doc 05).
7. **Is the skill rare or only needed now and then?** Rare, occasional skills: contractor. Common, daily skills: employee or tool.
8. **Do you have a person who could grow into it?** If yes and they want it, upskilling is cheaper and builds loyalty. If no, do not force it.
9. **How fast do you need it?** A tool or contractor can start in days. A hire takes weeks to months.
10. **What is the total cost over 12 months for each option?** Compare with the budget planner (doc 02).

## Quick matrix

| Work type | Likely best option | Why |
| --- | --- | --- |
| Reply to the same customer questions all day | Automation with human review of hard cases | High volume, rule based, low risk if reviewed |
| Book appointments and send reminders | Automation, plus a person for exceptions | Routine, clear rules |
| Bookkeeping data entry and bank matching | Software and a part time bookkeeper | Routine core, human judgment on exceptions |
| Build a website once | Contractor | One time project |
| Run payroll | Software plus an accountant or payroll provider | Costly errors, legal rules |
| Manage and coach a team | Employee | Trust, judgment, relationships |
| First sales hire who also shapes the offer | Employee (senior enough) | Judgment, learning the market |
| Occasional legal, tax, design work | Contractor or agency | Rare, specialist |
| Social posts for a small shop | Automation for drafts, owner or part timer to approve | Drafts are cheap, voice and truth need a human |

This matrix is a starting point. Every business is different. Always test with real examples before you decide.

## How to split one role into automated and human parts

Use a task inventory. Claude can build it with the owner in one short session, or from the scorecard's `automation_note` field.

| Task | How often | Hours per week | Rule based? | Cost if wrong | Sensitive data? | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| Answer common booking questions | Daily | 8 | Yes | Low | No | Automate, review a sample |
| Quote a custom job | Weekly | 4 | No | Medium | No | Human, AI drafts |
| Handle an angry customer | Rare | 2 | No | High | Maybe | Human only |
| Weekly schedule report | Weekly | 2 | Yes | Low | No | Automate |

This table is an example with made up numbers. The verdict values are:

- **Automate:** a tool does it, a human samples the output.
- **AI drafts, human decides:** the tool prepares, a person reviews every item.
- **Human only:** a person does it. Use AI only for notes or research that a person checks.

Then recompute the role: total hours that stay human, per week. If it is under about half a full time week, consider a part time person, a contractor, or a shared role.
If it is a full week of judgment heavy work, hire a full time person and write the scorecard around the human parts only.

## Automation payback (a fair check)

```
monthly_saving = hours_saved_per_month x hourly_value_of_that_work
monthly_cost   = tool_cost + (review_hours_per_month x hourly_value_of_reviewer)
net_per_month  = monthly_saving - monthly_cost
payback_months = setup_cost / net_per_month        (only if net_per_month is above zero)
```

Do not count a saving you will not use. If you save 10 hours a month but nobody can use that time, the saving is not cash.
Always include review time. Unreviewed automation is how small errors become big problems.

**Test before you decide.** Take 10 real examples of the task (with private details removed). Have the tool do them. A person grades each result.
If most are good enough with light review, automate. If many need rework, the task needs a human or a clearer description.
Do not trust a vendor claim or a demo alone. Test on your own cases.

## Do this

1. Write the need as outcomes (doc 05), not as a job title.
2. Make the task inventory and give each task a verdict from the decision procedure.
3. Estimate the human hours that remain per week.
4. Price each option for 12 months with `python3 tools/budget_planner.py` (the path "hire an outcome with AI plus a part time person" covers the combined option).
5. Run a small test of the automation part (the 10 example test) before you commit.
6. Decide who reviews automated work, how often, and who is accountable when it goes wrong. A named person, not "the team".
7. If you still hire, write the scorecard for the human parts only. The posting then attracts the right people and does not promise work that a tool will do.
8. Re check in 3 months: did the plan work? Move tasks between machine and human as you learn.

## Common mistakes

- Hiring first, then finding that half the job was routine and the person is bored in month 2.
- Automating a task that nobody has written down. The tool then does the wrong thing quickly.
- Automating work where a mistake is costly and nobody checks it.
- Hiding the automation from the new hire, or telling a candidate the job is something it is not.
- Replacing the human relationship in a place where trust is the product (care, advice, sales of big items).
- Using a contractor for the heart of the business, then losing the knowledge when they leave.
- Counting only tool cost and not setup and review time.
- Comparing the best case of automation with the worst case of a human, or the reverse.
- Treating "AI can do this" as a fact without testing it on your own examples.

## Numbers

All of these are formulas or starting assumptions. Do not read them as market statistics.

| Item | Starting assumption | Replace with |
| --- | --- | --- |
| Review time for automated output | 10 to 20 percent of the time the task used to take | Measure on your 10 example test |
| Setup time for a simple automation | A few hours to a few days | Your own first attempt |
| Hours that make a part time role worthwhile | About 10 to 20 hours a week | Whether you can recruit at that size locally |
| Contractor rate premium over an employee's hourly cost | Higher, depends on field and country | Real quotes from two contractors |

Funnel link: if the answer is "hire", go to docs 03 and 05. If the answer is "automate", write a one page plan (task, tool, reviewer, test result) in `hiring/<role>/plan.md`.

## Ask the owner

1. What work do you actually need done, in one sentence of outcomes? (Default: ask Claude to draft three, you pick.)
2. Which parts are routine and which need your judgment? (Default: Claude builds the task inventory from your answer.)
3. How costly is a mistake in this work? (Default: medium, so a human reviews every item at first.)
4. Is there data in this work you must keep private? (Default: yes, check doc 12 before using any tool.)
5. Is there someone on the team who wants to grow into this? (Default: no, so compare hire, tool and contractor.)
