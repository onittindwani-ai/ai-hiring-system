# Job post master template

Claude fills this in from your scorecard, then writes the shorter versions for each platform from it. Claude writes. You post by hand, in your own accounts. Claude never logs in to a job board for you.

How to use it:
1. Fill the placeholders from `hiring/<role>/scorecard.json` and your answers in `plan.md`.
2. Delete every guidance comment (the lines in `<!-- -->`) before posting.
3. Run `python3 tools/bias_check.py <file> --kind job-post` and fix what it flags.
4. Read it aloud once. If it sounds like a form letter, cut it.

---

# {{role_title}}

<!-- Title: the plain job title people search for. No hype nicknames. No code names, no city, no pay in the title. -->

**Company:** {{company_name}}
**Location:** {{location_or_remote_rule}}
**Type:** {{employment_type}} (full time, part time, contract)
**Pay:** {{pay_range}} {{pay_period}}
**Start date:** around {{start_date}}

<!-- Always include the pay range. Many places and many candidates expect it. Rules about pay transparency differ by region and change: checked on 2026-11-20, verify before relying on it. Not legal advice. -->

## What this job is, in one paragraph

{{mission_one_sentence}} In plain words: {{what_a_normal_week_looks_like}}.

<!-- One paragraph. Use the mission from the scorecard. Describe the work, not the perfect person. -->

## What you will do in your first 90 days

- {{outcome_1}}
- {{outcome_2}}
- {{outcome_3}}

<!-- 3 to 5 outcomes from the scorecard `outcomes_90_days`. Outcomes, not a list of tasks. -->

## What we are looking for

Must have (we cannot start without these):
- {{must_have_1}}
- {{must_have_2}}
- {{must_have_3}}

Nice to have (we will teach you if you do not have these):
- {{nice_to_have_1}}
- {{nice_to_have_2}}

<!-- Keep "must have" to 3 to 5 items, each tied to a `must` criterion. Every extra requirement makes some good people not apply. Never write wording that hints at age, gender, origin or background, and never ask for a photo or a degree you do not truly need. If a degree is not needed, say "no degree needed". -->

## How we hire

1. You apply with {{application_method}}. It takes about {{apply_minutes}} minutes.
2. We read every application ourselves. We look at job related answers first.
3. {{step_3}} (for example: a short call, then a short task of about {{work_sample_hours}} hours).
4. {{step_4}} (for example: a conversation with the team).
5. We aim to tell you our decision by {{decision_date}}.

If you need any adjustment to take part (a different format, more time, an accessible format), tell us at {{contact_email}}. We will help, and it does not count against you.

<!-- Say how many steps there are and how long it takes. People drop out of hidden or endless processes. -->

## About {{company_name}}

{{company_two_sentences}}

<!-- Two true sentences. No slogans. If you are small, say so honestly. -->

## What we offer

- {{benefit_1}}
- {{benefit_2}}
- {{benefit_3}}

<!-- Only things that are true and you will actually give. No invented perks. -->

## Equal opportunity

We make hiring decisions on skills, experience and how well the work fits. We welcome applicants of all backgrounds. {{equal_opportunity_wording_for_your_region}}

<!-- Use wording that is correct for your country or region. Ask a lawyer or employment adviser if unsure. Not legal advice. -->

## How to apply

{{apply_link_or_instructions}}

<!-- A form or email only. Do not ask for photos or other personal details that do not belong in an application (see the question rules in `templates/forms/screening-questions.md`). -->

---

## Checklist before you post (delete before publishing)

- [ ] Pay range is present and honest.
- [ ] Every "must have" matches a `must` criterion in the scorecard.
- [ ] No dashes of the long kind, no hype words, no age or gender words.
- [ ] The apply method works (test it yourself from a phone).
- [ ] Someone checked the post for legal and local rules that apply to you.
- [ ] You, not Claude, will post it.
