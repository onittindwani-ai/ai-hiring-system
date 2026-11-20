---
name: hiring-post
description: Writes the job post for each platform and builds the application form (Google Forms or Tally, or an Apps Script, or a manual form). Use when the user says job post, job description, application form, where should I post, or after the scorecard is approved.
---

# Hiring post and application form

Read `docs/knowledge/07-WRITING-JOB-POSTS-THAT-WORK.md` and `templates/job-posts/job-post-master.md`.

## The post

1. Write the master post from the approved scorecard and the plan: what the company does and why this role exists, the 90 day outcomes, the must haves (only real must haves, keep the list short), the pay range with its source, location and remote rules, how to apply and what happens next (steps and timing). Plain, warm, specific. Use the company's own tone from its website.
2. Run `python3 tools/bias_check.py <post.md> --kind job-post` and fix every flag (gendered words, age words, "ninja" words, "culture fit", missing pay range).
3. Make one version per platform the owner chooses (`templates/job-posts/`: LinkedIn, Indeed, Wellfound, Naukri, careers page, Google for Jobs JSON-LD). Save them in `hiring/<role>/drafts/`. Tell the owner the platform formats change, so check the fields before posting.
4. **The owner posts it by hand.** Say exactly where to paste each one. Claude never posts or logs in to a job board.

## The application form

Build from `templates/forms/application-form.json`, tailored with the scorecard's 3 screening questions (lawful, job related; no age, gender, photo, marital status or nationality questions). Include the privacy and consent question.

Ways to create it (ask which, default: whichever matches `browser_mode`):

1. **Browser mode (Claude in Chrome)**: say what you will open ("Google Forms, in your own signed in browser"), wait for a yes, build the form and a linked Sheet, show the share link and the Sheet link. If the page asks for a login or a CAPTCHA, stop and let the user do it. Do not touch any other tab.
2. **Apps Script**: `python3 tools/make_form_script.py templates/forms/application-form.json --out hiring/<role>/drafts/form.gs`, then give three plain steps to paste it at script.google.com and press Run. Works in any browser.
3. **By hand**: give the exact questions to paste into Tally, Google Forms or any form tool.

Tell the owner how applications reach you: export the Sheet as CSV into `hiring/<role>/inbox/`, or drop the exported file from the board. Then use `hiring-screen`.

## Rules

Nothing is published without a yes. No dashes in the post text. Never invent perks, numbers or promises. If pay is unknown, research it and ask; do not hide pay.
