# Careers page job post

The careers page on your own website is the most useful place for a job post, because you control the text, the form and the data. Claude writes the page text and the form. You (or your web person) publish it.

## Usual fields (check your website tool, formats change)

You decide the fields. A good careers page usually has: title, short summary, pay range, location or remote rule, type, what you will do, what we need, how we hire, a note about adjustments, and one apply button that opens the form from `templates/forms/application-form.json`. Add the Google for Jobs markup (`google-for-jobs.jsonld`) so the job can appear in search.

Use one page per job so each page can carry its own markup. Mark the job as closed or remove the page when it is filled.

## What Claude writes for you

1. The page text from the master template, in plain words.
2. The application form (Google Form script via `tools/make_form_script.py`, or the fields to paste into another form tool).
3. The `JobPosting` markup filled in for your job.
4. A short thank you page text for after the form is sent.

## Filled example (fictional company and role)

# Booking Coordinator

Northlight Home Services (a made up home repair and cleaning business) is looking for a Booking Coordinator.

**Location:** Springfield area, hybrid (3 days in the office)
**Type:** Full time
**Pay (made up for this example):** $22 to $26 per hour
**Start date:** around 1 March

## What you will do
Keep our booking schedule calm. You answer booking requests, confirm jobs with customers, and tell the crews what tomorrow looks like.

## What we need
- You stay organized with many moving parts.
- You write short, clear messages.
- You stay calm when plans change.

## How we hire
Fill in our short form (about 8 minutes). We read every application ourselves and look at job related answers first. Then a 20 minute call, a one hour scheduling task and a chat with the team. We aim to tell you within 2 weeks.

Need an adjustment to take part? Write to hiring@example.com.

**Privacy:** we use your answers only for this hiring process and delete them after the time stated in our notice (for example 6 months). You can ask us to delete them sooner.

[Apply now](https://example.com/jobs/booking-coordinator/apply) (made up link)

## What you must do by hand

- [ ] Publish the page and the form on your own site (or ask your web person).
- [ ] Test the apply flow on a phone and on a computer.
- [ ] Add the privacy notice and say how long you keep data. Not legal advice: check the rules for your region.
- [ ] Mark the page closed when the role is filled.
- [ ] Share the link yourself, in your own channels.

## Filling the Google for Jobs markup (`google-for-jobs.jsonld`)

The file is a template. Placeholders such as `{{company_name}}` are strings. Before you publish:

1. Replace every placeholder with a real value. `minValue` and `maxValue` must become plain numbers (no quotes), and `directApply` must become `true` or `false` (no quotes).
2. `datePosted` uses the format `2026-11-20`. `validThrough` uses the format `2026-12-20T00:00`. If the job does not expire, remove `validThrough`.
3. `employmentType` values are written in capitals: `FULL_TIME`, `PART_TIME`, `CONTRACTOR`, `TEMPORARY`, `INTERN`, `VOLUNTEER`, `PER_DIEM` or `OTHER`.
4. `unitText` is one of `HOUR`, `DAY`, `WEEK`, `MONTH`, `YEAR`.
5. For a fully remote job, remove `jobLocation`, add `"jobLocationType": "TELECOMMUTE"` and an `applicantLocationRequirements` block with the countries you accept (for example `{"@type": "Country", "name": "USA"}`). The page text must say it is fully remote.
6. Put the finished JSON inside `<script type="application/ld+json"> ... </script>` on the single job page. Every detail in the markup must also be visible on that page.
7. Test it with Google's Rich Results Test and the structured data help pages from Google Search Central.

Field names above follow Google's job posting structured data guide and schema.org `JobPosting` (checked on 2026-11-20, verify before relying on it: the guidance can change).

## Mistakes to avoid

- Marking up a page that is not a single job page, or one that no longer takes applications.
- Putting the pay estimate of someone else in `baseSalary`. Only your real pay belongs there.
- Leaving a filled job open. Remove the page or the markup, or set `validThrough` to a past date.
- Asking for personal details that do not belong in an application (see the question rules in `templates/forms/screening-questions.md`).
