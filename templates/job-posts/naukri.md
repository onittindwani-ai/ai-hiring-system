# Naukri job post

Claude writes this text. You post it by hand in your own Naukri recruiter account. Claude does not log in to Naukri, search its resume database or scrape it.

## Usual fields (check the platform, formats change)

Naukri is a large job board in India. Its recruiter form usually asks for: job title, location, experience range, salary range (you may be able to show or hide it), key skills, industry, department, role category, a description, and how many openings. Fields, limits and prices change, so open the form today and check. Do not trust a limit from memory.

If you can show the salary range, do. People trust posts with pay more. Where an experience range is a field, keep it honest and wide: a narrow range can shut out good people and may act as an age proxy. Think about whether you really need it.

## What Claude writes for you

1. A title and a short description in plain words.
2. A key skills list taken from the scorecard.
3. An experience note written as "what the person has done", not as a number of years where you can avoid it.
4. A screening questions list (lawful, job related).

## Filled example (fictional company and role)

**Job title:** Customer Support Executive
**Company:** Northlight Home Services (a made up home repair and cleaning business)
**Location:** Pune (office, 5 days)
**Openings:** 2
**Salary (made up for this example):** INR 3 to 4.5 lakh a year

**Job description**
Northlight Home Services needs two people to answer customers by phone, email and chat, solve their problems and pass bugs to the team.

Responsibilities:
- Answer customer questions and fix problems on the first reply where you can.
- Write clear, kind replies.
- Log repeated problems and suggest a fix.

What we need:
- You write clearly in English and one local language.
- You stay calm with upset customers.
- You learn tools fast.

**Key skills:** customer support, email writing, chat support, troubleshooting, CRM

**How we hire:** short form, a 20 minute call, a short reply writing task and a team chat. We aim to decide in 2 weeks.

Need an adjustment to take part? Tell us at hiring@example.com.

## What you must do by hand

- [ ] Sign in to Naukri yourself, create the post and approve any fee.
- [ ] Search the candidate database only in your own account and by the platform's rules. Export or copy what you find into `hiring/<role>/inbox/`. Claude reads it from there.
- [ ] Contact people yourself. Claude drafts the message, you send it.
- [ ] Follow India's rules on data and hiring. Not legal advice: check with an adviser.

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
