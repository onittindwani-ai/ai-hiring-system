# 07. Writing job posts that work, and the application form behind them

**Purpose.** A job post is a small piece of marketing and a small contract of honesty. This doc tells Claude how to structure a post,
show pay, use inclusive language, adapt it to each platform, and design the application form and its lawful knock out questions.

## What a good post does

1. A right person reads it and thinks "that is me". A wrong person reads it and thinks "that is not me", and moves on.
2. It is honest about the work, the pay, the hours and the place.
3. It makes applying easy and fair.

Short and specific beats long and vague. People decide in seconds, so the top third of the post carries most of the weight.

## Structure (the master post)

The master lives in `templates/job-posts/job-post-master.md`. Every platform version is built from it.

| Section | What goes in | Length guide (starting assumption) |
| --- | --- | --- |
| Title | The real job name people search for, plus place or type. No jargon, no "ninja" | 3 to 8 words |
| Pay and terms line | Pay range, hours, contract type, place or remote rules | One line near the top |
| Hook (2 to 3 lines) | Who you are in one honest sentence and why this role matters | 40 to 70 words |
| What you will do (outcomes) | 3 to 5 outcomes, in plain words, from the scorecard | 3 to 5 bullets |
| What we are looking for | 3 to 5 must haves and a few nice to haves, labelled | 5 to 8 bullets in total |
| What we offer | Real things: pay, schedule, learning, tools, location | 3 to 6 bullets |
| How we hire | Steps, timing, what the process looks like | 3 to 5 lines |
| How to apply | A link or button, how long it takes, what to expect | 2 lines |
| Accessibility and fairness note | How to ask for adjustments, equal opportunity line | 2 lines |

Order matters. Put pay and terms near the top. Put the process at the end so candidates know what happens next.

## Pay transparency

- **Put a pay range in the post.** It brings better matched applicants and fewer wasted conversations on both sides. The tool `bias_check.py --kind job-post` warns when pay is missing.
- **Use a real range**, the one you set in doc 05. Do not write "competitive". Do not use a range so wide it says nothing.
- **State the unit:** per hour, per month, per year, and the currency.
- **Variable pay or benefits:** say what is fixed and what depends on results. Do not promise what you cannot deliver.
- **Laws.** Some places require pay ranges in job posts, and some limit questions about past pay. Rules differ by place and change. Not legal advice. Check doc 12 and a local source before posting.
  For any specific rule, name the primary source and write "checked on 2026-11-20, verify before relying on it". This doc does not state any specific local rule.

## Inclusive language (practical rules)

1. **Write about the work, not the person.** Say "you will handle customer questions", not "we need a young, energetic person".
2. **Avoid age, gender and background signals:** "digital native", "recent graduate" for a role that is not entry level, "he", "salesman", "native speaker", "mature", "energetic".
   Say "fluent in English" only if the job needs it, and say why ("write customer emails in English").
3. **Avoid vague culture words:** "culture fit", "work hard play hard", "rockstar", "ninja", "guru". Describe behaviours instead ("comfortable with changing priorities").
4. **Keep requirements short and honest.** Long lists of must haves discourage strong applicants who would learn the rest fast.
5. **Mark what can be learned.** "You do not need to know our booking software, we will teach you."
6. **State the physical or time demands** only if the job really has them, and offer adjustments where possible.
7. **Accessibility:** use plain text, short paragraphs, descriptive links, no text inside images, and give another way to apply (email or phone) for people who cannot use the form.
8. **Equal opportunity line:** a short, honest sentence. Do not copy a legal text you have not checked.
9. **Run the checker:** `python3 tools/bias_check.py hiring/<role>/drafts/post.md --kind job-post`. Read each line it flags and fix or explain.

Words and phrases the checker looks for are in `data/banned_terms.json`. It is a help, not a guarantee. A human reads the post last.

## Platform formats

Each platform has its own file in `templates/job-posts/`. Claude fills them from the master and the scorecard.

| File | Use for | Notes |
| --- | --- | --- |
| `job-post-master.md` | The source of truth for the post | Build all others from it |
| `linkedin.md` | A LinkedIn job post, written for the user to paste | User posts by hand. Claude never drives LinkedIn |
| `indeed.md` | An Indeed job post | User posts by hand |
| `wellfound.md` | A Wellfound (startup) post | Often more about mission and team size |
| `naukri.md` | A Naukri post | Follow the platform's fields and keywords |
| `careers-page.md` | Your own website careers page | Fuller version, with your story and process |
| `google-for-jobs.jsonld` | Structured data so a careers page can appear in Google job search | Needs a careers page you control. Check Google's current documentation for job posting structured data before relying on it |

Platform limits, fields and fees change. When you post, read the current form and adjust. If a platform shows a character count, use it.
Keep one core text and change only the title, the order, the length and the tags per platform. Do not post different pay on different platforms.

## Application form design

The form is a filter and a first impression. The template is `templates/forms/application-form.json`, and the screening questions are in `templates/forms/screening-questions.md`.
`python3 tools/make_form_script.py templates/forms/application-form.json --out form.gs` writes a Google Apps Script the user can paste at script.google.com to create the form and a linked sheet.
This works without any browser extension. If the user has Claude in Chrome on their own Google account, Claude can help set up the form in the user's own Forms. Safari and Firefox users can use manual mode (Claude writes, the user clicks).

### Design rules

1. **Short.** Aim for 5 to 10 minutes. Starting assumption. Every extra field loses applicants.
2. **Collect only what you need.** Name, email, a phone only if you will call, a city or region (for logistics, not for judging), and a resume or a link to work.
3. **Make the resume optional if you can.** A short answer set and a work link often tell you more than a resume. Some strong people have no resume.
4. **Three screening questions, job related.** Each ties to a criterion in the scorecard. Ask for a real example, 50 to 150 words. Examples of style (made up for Northlight): "Describe a time you had to reschedule many customers at once. What did you do first, and what happened?"
5. **Do not ask for a long cover letter.** It rewards polish over skill.
6. **Mobile friendly.** Many people apply from a phone.
7. **Accessible.** Plain labels, no required fields that are not needed, another way to apply, and a contact for adjustments.
8. **Consent and privacy note.** One short paragraph: what you collect, why, how long you keep it, who sees it, how to ask for deletion. Details and legal checks in doc 12.
9. **Equal opportunity data** (if you collect it at all) goes in a separate, optional section and is never used in scoring or shown to scorers.
10. **No photo, no age, no date of birth, no marital status.** Never.
11. **Confirmation message.** Tell the applicant what happens next and when.

## Knock out questions (lawful ones)

A knock out question is a yes or no (or a simple fact) that decides whether a person can move forward. It must be job related and necessary for the job.
Here "lawful" means designed to be job related; the law differs by place, so check doc 12 and a local source. Not legal advice.

| Type | Lawful style (job related) | Avoid |
| --- | --- | --- |
| Right to work | "Are you legally allowed to work in [country] for this role?" (ask everyone the same way) | Asking about citizenship, nationality or origin |
| Schedule | "This role works Saturdays 8 to 14. Can you work that schedule?" | "Do you have young children?" |
| Licence or certification | "This role requires a valid [licence] to drive our van. Do you hold one?" | Asking for a licence the job does not need |
| Location | "This role is on site in [city]. Can you work on site there?" | "Where are you from?" |
| Physical demands | State the real demand and ask if they can do it with or without adjustment | Asking about health, medical history or disability |
| Pay | "What pay range are you looking for?" | Asking for past pay history (restricted in some places, verify) |
| Language | "This role needs you to write customer emails in English." | Asking for a native speaker or the languages someone grew up with |

Rules for gates:

1. Every gate has a written job related reason in the scorecard (`gates` and `deal_breakers`).
2. A gate answered "no" or "unknown" goes to a human. Claude does not reject anyone, and the score tool never writes "rejected".
3. Ask the same gate questions of everyone.
4. Prefer a gate that can be met with an adjustment over a hard no. Offer a way to ask for one.
5. Do not use a knock out for a skill you can score instead. Score skills, gate facts.

## Do this

1. Start from the scorecard, not from a template post.
2. Write the master post with pay and terms near the top. Keep it under about 400 words (starting assumption).
3. Run `bias_check.py`, fix the flags, and read the post aloud.
4. Build the platform versions. Give the user the text. The user posts.
5. Build the form from `application-form.json`. Keep it under 10 minutes. Test it yourself on a phone.
6. Add the privacy note and a way to ask for adjustments.
7. Add a tracking source to each link (for example `?source=careers`), so you know which channel brings finalists (doc 06).
8. Keep the post live and current. Close it with a clear message when filled.

## Common mistakes

- A vague title and a vague mission.
- "Competitive salary" and no number.
- A requirements list that no real person could meet.
- Gendered or age loaded words ("he", "young", "digital native", "rockstar").
- A long cover letter and a 40 field form.
- Asking for things you cannot lawfully use (age, photo, family plans, health).
- A form that does not work on a phone.
- Different pay in different places.
- A post that promises remote work and then requires three days in the office.
- No reply to applicants after they apply.

## Numbers

| Item | Starting assumption | Replace with |
| --- | --- | --- |
| Post length | Under about 400 words | Your own tests |
| Form time | 5 to 10 minutes | Time yourself and one friend |
| Screening questions | 3 | What the scorecard needs |
| Answer length | 50 to 150 words | The role |
| Time to first reply to an applicant | 3 working days | Your capacity |

If many applicants start but do not finish the form, the form is too long or too hard. If applicants finish but are poor fits, the post is vague or pay is missing.
These are signs to read, not statistics.

## Ask the owner

1. What is the pay range, in what unit and currency? (Default: Claude shows the research to do, you set it.)
2. Is the job on site, hybrid or remote, and where? (Default: on site where your business is.)
3. What must a person be able to do on day one, and what can they learn? (Default: three musts, the rest nice to have.)
4. Do you want a resume at all, or short answers and a work link? (Default: optional resume, three short answers.)
5. Is there another way for someone to apply (email, phone)? (Default: yes, an email address at your own domain.)
