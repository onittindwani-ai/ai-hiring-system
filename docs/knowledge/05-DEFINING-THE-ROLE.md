# 05. Defining the role

**Purpose.** A clear role is the single best predictor of a smooth hire. This doc shows Claude how to turn a vague need into a mission,
outcomes, must haves and nice to haves, a level and a pay range, and how to write them into the scorecard that every later step uses.

## The building blocks

| Block | What it is | Example (made up) |
| --- | --- | --- |
| Mission | One sentence on why the role exists | "Make sure every booking request gets a clear answer within one working day." |
| Outcomes (90 days, 12 months) | What success looks like, measurable | "By day 90, all new requests get a reply within 8 working hours." |
| Criteria | The skills and evidence you will score | "Scheduling under pressure", "Clear written messages" |
| Must haves | Needed on day one, or the role fails | "Can work the shift pattern" |
| Nice to haves | Helpful, can be learned | "Knows our booking software" |
| Level | How independent and how senior | Entry, mid, senior, lead |
| Scope | What is in and out of the role | "Not responsible for payroll" |
| Pay range and terms | Money, hours, location, contract type | See below |

All of this lives in the scorecard (`templates/scorecards/*.json`, checked with `python3 tools/validate_scorecard.py`).
The scorecard is not a job ad. It is the private source of truth that the ad, the form, the screening and the interview questions are built from.

## Outcomes, not tasks

Tasks tell people what they will do. Outcomes tell them what good looks like. Tasks attract people who follow lists.
Outcomes attract people who deliver results, and they give you a fair way to judge a hire after 90 days.

| Task style (weak) | Outcome style (better) |
| --- | --- |
| "Answer phones and emails" | "Every inbound request gets a clear reply within one working day" |
| "Do the books" | "Books closed within 5 working days after month end, with no unexplained items" |
| "Post on social media" | "Four useful posts a week that bring in enquiries we can track" |
| "Write code for the app" | "Ship the booking API changes by day 60, with tests, and no urgent bugs open longer than 2 days" |

The numbers in these examples are made up. Use real numbers from your business, or say "to be set with the manager in week 2".

## Do this

1. **Write the mission in one sentence.** If you cannot, the role is not ready. Ask: "If this person did only one thing well, what would it be?"
2. **List 3 to 5 outcomes for the first 90 days.** Each measurable, each something a manager can check.
3. **List the criteria.** The scorecard needs 5 to 8. Pick the few things that really separate great from average in this role.
4. **Mark must versus nice.** A must is something the person cannot learn fast enough or the role fails without. At least 3 must criteria; the tools expect it.
5. **Set a minimum level per must criterion** (0 to 4 scale from the scorecard: 0 no evidence, 1 mentioned only, 2 did it with help, 3 did it on their own, 4 did it and taught or improved it).
6. **Weights add to 100.** Each between 5 and 30. A heavy weight on one criterion tells everyone what really matters.
7. **Add gates and deal breakers only when job related.** A gate is a simple fact (can they work in the country, can they work the needed shift). A deal breaker needs a written job related reason.
8. **Set the level and scope** (see below). Write what the role does not own.
9. **Research pay** (see below) and set a range before you post.
10. **Write interview questions per criterion** and a short work sample if the role needs one. Validate the file with `python3 tools/validate_scorecard.py`.
11. **Read it as a candidate would.** Is it honest, clear, and not a wish list for three people?
12. **Freeze it** before sourcing starts. Change it only with a written reason and tell everyone who is scoring.

## Must versus nice, and the "unicorn" trap

Test every must have with this question: "If a great person lacked this on day one, could they learn it within 60 days?"
If yes, it is a nice to have. A long list of musts shrinks the pool and often excludes strong people who learn fast.
The tools also warn about long requirement lists, because long lists hurt some groups of applicants more than others and rarely help the hire.

Use years of experience carefully. Years are a weak stand in for skill. Ask for evidence of the thing instead (a shipped project, a result, a sample).
Never set a number of years "older than the role needs" or phrases that signal age (see doc 07 and `data/banned_terms.json`).

## Level

Define level by what the person does without help, not by years or titles.

| Level | Independence | Typical scope | What to look for |
| --- | --- | --- | --- |
| Entry | Needs guidance, follows a clear process | One task area | Potential, reliability, learning speed, basic skill shown by a sample |
| Mid | Works alone on normal work, asks on hard cases | Own a set of tasks end to end | Past results at this level, good judgment on routine problems |
| Senior | Owns a whole area, helps others | A team's outcomes | Examples of hard decisions and results, teaching |
| Lead or manager | Owns people and results | A team or function | Examples of building a team, handling conflict, hiring |
| First hire or key early hire | Builds the role itself | Unclear and changing | Comfort with ambiguity, breadth, trust (doc 13) |

Hiring above the budget level is a common trap. Hiring below the level you need and hoping they grow is the opposite trap. Decide with the budget in mind (doc 02).

## Scope creep (the role that keeps growing)

Write what the role does not do. Review the list every month in the first six months.
Warning signs: you add "also" to the job post three times, the post lists five different tools, or the mission has "and" more than once.
When that happens, split the role into two (a core and a support part) or choose the one that matters most. Doc 04 shows how to split human and automated parts.

## Pay and level

1. **Find the market range.** Use at least three real sources: pay ranges in posts for similar roles in the same place, a salary survey from a professional body or a government labour statistics site, and one or two honest conversations with peers. Write the source and date in `plan.md`. The scorecard field `pay_research_hint` tells you where to look. Claude cannot invent numbers.
2. **Set a range, not one number.** Entry points at the lower part, strong at the top. Decide ahead what you would pay for a person who meets all musts and one who exceeds them.
3. **Check internal fairness.** Do not offer more than a current employee earns in the same role without a plan. Pay differences should come from job related reasons.
4. **Decide the terms:** full time or part time, permanent or fixed term, hours, shift pattern, on site, hybrid or remote, location rules, start date, notice period.
5. **Remote and location.** Write whether the person must be in a place, in a time zone window, or can be anywhere. Doc 14 covers remote and cross border hiring and the questions to ask an expert.
6. **Seniority and urgency.** The more senior and the more urgent, the more you pay in time or in money (doc 02). Urgent plus tiny budget plus senior is a hard combination. Say so.

Pay transparency laws and rules differ by place and change. See doc 07 and doc 12. Not legal advice.

## Company stage changes the role

| Stage | What the role needs | Typical risk |
| --- | --- | --- |
| Just the owner, first hire | A generalist who builds the job | Unclear role, owner overloaded |
| Small team (under about 15) | Doers who can switch tasks | No process, one person is a single point of failure |
| Growing company | Specialists and some managers | Hiring too fast, culture drift |
| Established | Defined roles, defined levels | Slow decisions |

Stages are a rough guide. Do not use them as a fixed label.

## Common mistakes

- A job title with no mission ("Marketing Ninja", "Office Hero").
- Copying a big company's job ad for a team of ten.
- Ten musts and no nice to haves, or the reverse.
- Weights that sum to 100 but treat everything the same, so the scorecard tells you nothing.
- Asking for "culture fit" or "digital native". These are proxies for who someone is, not for the job. Use specific behaviours instead (for example "works well with changing priorities").
- Setting pay after the candidate asks. Decide the range first.
- Letting the interview team invent new criteria on the day.
- Writing the role for a person you already know, then posting it as an open search.
- Forgetting to say what the person will not do.

## Numbers

| Item | Rule or starting assumption |
| --- | --- |
| Criteria per scorecard | 5 to 8 |
| Must criteria | At least 3 |
| Weights | Integers 5 to 30, sum 100 |
| Keywords per criterion | 4 to 12 |
| Outcomes for 90 days | 3 to 5 |
| Work sample length | 30 to 60 minutes, starting assumption (shorter is fairer) |

The score formula the tools use: `weighted_score = sum(weight x level / 4)`, giving 0 to 100.
The scorecard is checked with `python3 tools/validate_scorecard.py <file>`. Language in the job post is checked with `python3 tools/bias_check.py <file> --kind job-post`.

## Ask the owner

1. What is the one thing this person must do well? (Default: Claude proposes a mission, you edit it.)
2. What does success look like after 90 days? (Default: Claude drafts three outcomes, you adjust.)
3. What is the pay range and where did it come from? (Default: Claude shows the research sources to check, you give the range.)
4. On site, hybrid or remote, and in which place or time zone? (Default: on site where your business is.)
5. What must they be able to do on day one, and what can they learn? (Default: three musts, the rest nice to have.)
