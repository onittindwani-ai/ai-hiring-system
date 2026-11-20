# LinkedIn job post

Claude writes this text. You post it by hand in your own LinkedIn account. Claude does not log in to LinkedIn, post for you or scrape it.

## Usual fields (check the platform, formats change)

LinkedIn's job form usually asks for: job title, company, workplace type (on site, hybrid, remote), job location, job type, a description, skills, and how people apply (LinkedIn easy apply, or your own link). It may also show a pay field. Character limits and field names change, so open the form and check what it shows today. Do not trust any number from memory, including ours.

## What Claude writes for you

1. A short title that matches what people search.
2. A description in plain text with short paragraphs and simple bullets (rich formatting may not carry over, so keep it simple).
3. A list of 5 to 10 skills to tick, taken from the scorecard `must` criteria.
4. Three screening question ideas (lawful and job related, see `templates/forms/screening-questions.md`).

## Filled example (fictional company and role)

**Title:** Booking Coordinator

**Company:** Northlight Home Services (a made up home repair and cleaning business)
**Location:** Springfield area, hybrid (3 days in the office)
**Type:** Full time
**Pay (made up for this example):** $22 to $26 per hour

Northlight Home Services books home repair and cleaning jobs for about 14 people across two cities. Our bookings are growing, and we need one person to keep the schedule calm.

What you will do:
- Answer booking requests by phone and email and put every job in the calendar.
- Confirm each job with the customer the day before and move jobs when plans change.
- Tell the crews each evening what tomorrow looks like.
- Write down the five most repeated problems each month and suggest a fix.

What we are looking for:
- You keep many moving parts straight, with a calendar and a checklist you trust.
- You write short, clear messages to customers and crews.
- You stay calm when plans change.
- Nice to have: you have used scheduling software or spreadsheets. We will teach the rest.

How we hire: apply with the short form (about 8 minutes). We read every application ourselves. Then a 20 minute call, a short scheduling task (about 1 hour), and a chat with the team. We aim to decide within 2 weeks of your application.

Need an adjustment to take part? Tell us at hiring@example.com.

Apply here: https://example.com/jobs/booking-coordinator

## What you must do by hand

- [ ] Sign in to your own LinkedIn account and create the job post.
- [ ] Paste the text, tick the skills, set the screening questions, publish.
- [ ] Check what it costs before you confirm. Paid posts spend money, so only you approve that.
- [ ] Export or copy the applications you get into `hiring/<role>/inbox/` for Claude to read.
- [ ] Message people yourself. Claude drafts, you send.

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
