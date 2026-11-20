# Indeed job post

Claude writes this text. You post it by hand in your own Indeed employer account. Claude does not log in to Indeed or scrape it.

## Usual fields (check the platform, formats change)

Indeed's employer form usually asks for: job title, location, job type, schedule, pay (a range and a period), benefits, a description, whether people apply on Indeed or on your site, and a few screening questions. Sponsored (paid) options usually exist next to a free listing. Rules, fields and limits change often, so check the form today. Do not trust a number from memory.

Indeed shows pay prominently, so give a real range. Plain, short descriptions with clear headings and bullet lists usually read best on a phone.

## What Claude writes for you

1. A title that matches how people search (no codes, no city in the title).
2. A description with short sections: the job, what you will do, what we need, pay and schedule, how we hire.
3. Pay and schedule lines ready to type into the form fields.
4. Screening questions that are lawful and job related (not age, gender, nationality, family status or photo).

## Filled example (fictional company and role)

**Job title:** Booking Coordinator
**Location:** Springfield area (hybrid)
**Job type:** Full time
**Pay (made up for this example):** $22 to $26 an hour
**Schedule:** Monday to Friday, day shift, one Saturday a month

**About the job**
Northlight Home Services (a made up home repair and cleaning business) needs one person to keep the booking schedule running smoothly for a team of 14.

**What you will do**
- Answer booking requests and put every job in the calendar.
- Confirm jobs with customers the day before.
- Tell the crews the plan each evening.
- Suggest one improvement a month.

**What you need**
- A way to stay organized with many moving parts.
- Clear, friendly writing for customers.
- Calm when plans change.

**How we hire**
Short application form, a 20 minute call, a one hour scheduling task and a team chat. We aim to decide within 2 weeks.

Need an adjustment to take part? Tell us at hiring@example.com.

## What you must do by hand

- [ ] Sign in to Indeed yourself and create the post.
- [ ] Choose free or sponsored. Sponsored costs money, and you approve the budget.
- [ ] Add the screening questions from `templates/forms/screening-questions.md`. Do not mark any question as an automatic "reject" answer. A person reviews every application.
- [ ] Download or copy applications into `hiring/<role>/inbox/` for Claude to read. Claude does not collect them from Indeed.
- [ ] Reply to candidates yourself.

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
