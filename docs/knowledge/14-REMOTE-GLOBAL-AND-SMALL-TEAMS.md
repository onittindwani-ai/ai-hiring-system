# 14. Remote, global and small teams

## Purpose
Hire people who work from another place, another time zone or another country, and do it well with a team of 1 to 20.
Mistakes here are expensive: a wrong time zone, a wrong contract type, a wrong pay logic. This doc gives the questions to settle first.
**Not legal advice.** Hiring across borders is the area most likely to need a local expert. Verify locally.

## Do this
1. Decide where the work can be done: on site, hybrid, remote in your country, remote anywhere. Write the real rule in the post. If hybrid or on site, say the city and the days.
2. Decide the hours that must overlap. "Remote" does not mean "any hours". State the overlap in the post (for example "at least 4 hours between 9 and 5 in your own time zone, overlapping with ours").
3. Decide the working language and the level needed for the job. Do not score accent. Test the level the job needs through a work sample (doc 10).
4. Decide employee, contractor, or employer of record for each person (next section). Ask a local expert before you hire in a new country.
5. Build pay with a stated logic (pay across regions). Use the same logic for everyone in the same role.
6. Write down how work will happen: tools, communication, async rules, meeting times, response times, how to ask for help.
7. Make the first month very clear. Remote people feel lost faster. Give a buddy and a 30 60 90 plan (doc 11).
8. Protect data: laptops, accounts and access, passwords through a manager, limited permissions at first (doc 12).
9. Review how it is working at 30, 60 and 90 days, and ask the person what is hard.

## Employee, contractor or employer of record (concepts)
| Option | What it means | Good when | Watch out |
| --- | --- | --- | --- |
| Employee | you employ them directly under local labour law | the work is ongoing, you manage how and when it is done, you are in the same country | each country has taxes, social contributions, notice, leave; setup in another country can mean a local company or registration |
| Contractor (freelancer, independent) | they run their own business and invoice you for an outcome | a defined project, they choose how to work, they work for others too | **misclassification**: if the work looks like employment, the law may treat them as an employee; fines and back payments are possible |
| Employer of record (EOR) | a company in that country legally employs the person on your behalf; you direct the daily work and pay the EOR a fee | you want a real employee in a country without opening an entity | cost of the fee; contract terms; you still manage fairly; check what the EOR handles and what remains yours |
| Part time employee | a smaller version of employee | ongoing smaller needs | same law as employee |
Misclassification: tests differ by country and state. Signs the law may call them an employee: you set their hours, give detailed instructions, provide the tools, the work is central to your business, they work only for you, or the relationship is long and open ended. Do not label someone a contractor only to save money. Verify locally. Costs of getting it wrong are real, but no number is given here because it differs by place.
- What the owner can do: a short written contract, a clear scope, an invoice by the contractor, no control over how they work beyond the outcome, and a local adviser's review for any long term arrangement.
- If you hire in India, the owner should ask a local adviser about the applicable rules, taxes and contract form. This doc did not verify them.

## Time zones and async
- Pick a core overlap window and make everything else async. Overlap windows of 3 to 4 hours work for many teams (starting assumption).
- Write things down: decisions, tasks, why. If it was only said on a call, it did not happen.
- Async rules: where each kind of message goes, how fast to reply (for example within 1 working day), what is urgent and how to flag it.
- Meetings: rotate unfair times so one side is not always at 6am or 11pm. Record notes, not whole calls.
- Handoffs: end of day notes with status, blockers and the next step.
- Use dates with the time zone, written the same way every time.
- Tell candidates the time zone rules before the first call.

## Pay across regions
Two defensible approaches. Pick one, write it down, apply it to everyone.
1. Pay for the role and level, same for everyone, wherever they live. Simple, fair, expensive in lower cost places, but easy to explain.
2. Pay by location bands: a base for the role, adjusted by a location factor from a published source. More complex; people may feel it unfair when they do the same work.
Rules for either:
- Use real market data with a source and a date (`pay_research_hint`). Do not invent a "global rate".
- Pay in a currency the person can use, and say who pays the transfer fees and when. Confirm the exchange logic, and who bears currency risk.
- Do not set pay by what they earned before. Use the role's range.
- In places with pay transparency rules, show the range in the post (doc 12).
- Taxes, social contributions and mandatory benefits differ. For employees these are an employer cost on top of pay (`tools/budget_planner.py --employer-cost-pct` prints the assumption you set). For contractors, the contractor handles their own taxes, as the law allows (verify locally).
- Write down review dates and rules for raises, so it does not turn into negotiation by whoever asks loudest.

## Hiring in other countries: checklist
1. Is the person legally allowed to do this work from where they live? Verify. Do not ask nationality. Ask "are you legally able to work from {{country}} for this role?".
2. Which contract form fits (table above)? Ask a local expert.
3. Tax and registration: do you need a local entity or registration? An EOR may remove that need.
4. Payroll: how and when they are paid, in which currency.
5. Labour law: notice, leave, hours, probation. These differ widely. Do not copy your own country's rules.
6. Data protection: if you hold data of people in the EU or other regions, their rules may apply to you (doc 12).
7. Equipment, insurance, security, and who owns the work they produce (put it in writing).
8. Visa and moving: do not promise sponsorship you cannot give. If the person must relocate, ask a lawyer.
9. Holidays: learn the local holidays and put them in the calendar.
10. Export or sanctions limits can restrict hiring or paying someone in some places. Ask a lawyer.

## Small team realities (1 to 20 people)
- Every hire is a big share of the company. A miss is costly, and so is a slow decision.
- You have no HR team. The owner is the recruiter, the manager and the onboarding guide. Block time on the calendar for it.
- Process should be light: one scorecard, one form, one pipeline file, one 30 minute weekly review (`tools/pipeline.py weekly`).
- Say clearly what you can and cannot offer: growth, titles, benefits, stability. A small team that is honest wins people who like small teams.
- You cannot out pay a big company. Compete on clear work, trust, learning, flexibility and speed. Never promise more than you can give.
- Be careful with friends and family hires. Use the same scorecard, and decide who makes the call.
- Plan for single points of failure: one person who knows everything is a risk. Write things down.
- Cash is tight: use the budget planner, and hire or automate first (docs 02 and 04).
- Hire slowly, but decide fast once you have the evidence.

## What to look for in a remote worker
Write these as job related criteria and test them with a work sample, not a guess.
- Writes clearly and asks good questions when blocked.
- Plans their own day and finishes work without being chased.
- Gives updates before being asked.
- Handles feedback in writing.
- Has a workable setup (internet, a quiet enough place) or says what they need. Never judge a home, a background or family noise.
Ask a trial question: "Tell me about a project you ran from start to finish with little supervision. How did people know where it stood?"

## A light toolset for a tiny remote team
- One place for tasks (a shared sheet or simple board), one place for chat, one place for documents, one calendar.
- One written "how we work" page: hours, reply times, who decides what, how to ask for time off.
- One weekly 30 minute meeting, one monthly one to one on growth. Cut the rest.
- Keep it boring and consistent. Tools are not culture.

## Founder mistakes
- Hiring only people like yourself.
- Waiting too long to write the real job down, then hiring a "generalist" who is unclear on the work.
- Hiring in a hurry because things are on fire.
- Making a person a contractor while treating them as staff.
- No onboarding. "Just jump in" is not onboarding.
- Promising equity, titles or raises in chat and not writing them down.
- Hiring one person to fix a problem that is really about process or pay.
- Picking a time zone without checking the work needs real time overlap.
- Setting pay by haggling instead of a logic.
- Letting a high performer behave badly because they are productive.
- Not reviewing the fit at 30, 60 and 90 days.
- Posting jobs with a vague "remote" and getting 500 applicants who cannot work your hours.

## Common mistakes (remote and global)
- Leaving out the time zone, hours and language in the post.
- Assuming remote means 24 hour availability.
- Using one country's labour rules everywhere.
- Mixing up contractor and employee.
- Ignoring local holidays and local pay norms.
- Sharing too many accounts and files on day 1.
- Not asking the person what makes remote work hard for them.

## Numbers
- Overlap window: start with 3 to 4 hours (starting assumption, replace with your own data).
- Reply time for async: within 1 working day (starting assumption).
- Employer cost on top of pay for employees: set with `tools/budget_planner.py --employer-cost-pct P`. Use a number from a local source, not a guess. The tool prints your assumption.
- EOR fee: use a quote from the provider. No number is given here because prices vary and change.
- Check ins: weekly one to one, 30 60 90 reviews.

## Ask the owner
1. Where must the person live or work? Default: same country and a time zone within 3 hours of yours.
2. Which hours must overlap? Default: 4 hours in the middle of both working days.
3. Employee, contractor or EOR? Default: employee in your own country, contractor only for defined projects, EOR only after you get a quote and a local adviser's view.
4. How will pay be set across places? Default: the same range for the role, wherever they live.
5. Who handles onboarding and the first 90 days? Default: the owner, with a written 30 60 90 plan and a buddy if you have one.
