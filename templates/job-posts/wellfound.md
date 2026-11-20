# Wellfound job post

Claude writes this text. You post it by hand in your own Wellfound (formerly AngelList Talent) account. Claude does not log in to Wellfound or scrape it.

## Usual fields (check the platform, formats change)

Wellfound is mostly used by startups and small tech teams. Its job form usually asks for: title, job type, location or remote rule, pay (often a range and sometimes equity), skills, experience level, a description and a short company profile. The platform changes its fields and its pricing from time to time. Open the form today and check what it asks for before you trust this list.

Candidates there often look for pay, equity details, remote rules and how the team works. Be specific about those.

## What Claude writes for you

1. A description with a short "why this role exists" paragraph, outcomes, must haves and how you hire.
2. The pay line, plus an honest equity sentence if you offer equity. If you do not offer equity, say so.
3. A short team and way of working paragraph (hours, tools, meetings).
4. A skills list from the scorecard.

## Filled example (fictional company and role)

**Title:** Operations Coordinator
**Company:** Northlight Home Services (a made up home repair and cleaning business)
**Location:** Remote friendly within one time zone band, with a monthly visit to the office
**Type:** Full time
**Pay (made up for this example):** $48,000 to $58,000 a year. No equity.

**Why this role exists**
We book repair and cleaning jobs for two cities, and our schedule is growing faster than our spreadsheets. You would own the schedule and the checklists.

**In the first 90 days**
- Take over the weekly schedule and job tracker.
- Reduce late or missed jobs with reminders and a simple checklist.
- Write short guides for our five most repeated tasks.

**What we need**
- You stay organized and follow up until things are done.
- You write short, clear updates.
- You are comfortable with spreadsheets and learning new tools.

**How we work:** a small team of 14, a short daily check in, written updates in a shared channel.

**How we hire:** short form, a 20 minute call, a one hour task and a team chat. A decision within 2 weeks.

Apply: https://example.com/jobs/operations-coordinator (made up link)

## What you must do by hand

- [ ] Sign in to Wellfound yourself and post.
- [ ] Check the cost and the terms of the plan you pick. You approve any spend.
- [ ] Read and answer messages yourself, or copy them into `hiring/<role>/inbox/` for Claude to help draft replies.
- [ ] Do not let anyone or any tool send mass messages from your account without your approval of each message.

## Wording tips that work on any board

- Open with the job and why it exists, not with a long company history.
- Put the pay range near the top.
- Use "you will" sentences about outcomes. Cut any requirement you would not reject someone for.
- Keep the "must have" list to 3 to 5 lines. Put the rest under "nice to have".
- Say how many steps the hiring process has and how long it takes.
- Add one line about adjustments for people who need them.

## Mistakes to avoid

- Hype nicknames for the job or the team (they put off good people and some signal bias).
- Any wording that hints at age, gender, origin or a person's background, even softly. Describe the work and the skill instead.
- A long list of tools nobody needs on day one.
- Hiding the pay or the location rule.
- Posting a job you are not ready to answer. Reply times matter to candidates.

Run `python3 tools/bias_check.py templates/job-posts/<your-file>.md --kind job-post` before you post.
