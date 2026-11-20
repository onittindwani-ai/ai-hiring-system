# 06. Sourcing playbook

**Purpose.** Sourcing is how the right people find out about the job. This doc lists every channel, says who runs it (Claude or the user),
what effort it takes, what quality to expect and what to watch for, and gives a first week plan.

## The rule that governs this whole doc

Claude never drives, scrapes or logs in to LinkedIn, Indeed, Naukri, Wellfound or any other job board or social network, in a browser or by code.
The user runs searches in their own account, then exports or pastes the results into `hiring/<role>/inbox/`.
The user posts jobs and sends messages by hand. Claude writes the search strings, the job posts and the messages, and processes the pasted or exported results.
Claude may run ordinary web search (Google style) and read the public snippets it returns. Claude in Chrome is only for the user's own tools (their forms, sheets, calendar, email, company website).
Nothing is sent, posted or contacted without the owner's yes. This is not legal advice (doc 12).

## Channel list

Effort is the owner or manager's time, in hours per week at a normal pace. Quality describes how often candidates from this channel fit, which varies by role, place and how well you write the post.
These are planning guides, not statistics.

| # | Channel | Who runs it | Effort | Expected quality | Compliance and care |
| --- | --- | --- | --- | --- | --- |
| 1 | Inbound job boards (general and local) | User posts. Claude writes the post | Low | Wide reach, mixed fit, lots of noise | Follow each board's current rules and fees. Add pay range. Honest post. |
| 2 | Niche boards and professional bodies | User posts. Claude writes the post | Low | Smaller pool, often better fit | Check the board's terms. Pay and fees vary. |
| 3 | Your own careers page and website | User (or Claude in Chrome on the user's own site tools) | Low | Fit is high if people already know you | Keep the page current. Include how to apply and privacy note. |
| 4 | Referrals from staff and friends | User asks. Claude writes the ask | Low | Often high, but can repeat the same kind of person | Do not promise a bonus unless it is real. Same scorecard for every referral. Avoid only hiring "people like us". |
| 5 | Google X-ray search of public web pages | Claude runs through web search. Public snippets only | Medium | Good for niche skills. Hit rate varies | Only public snippets. Do not open or scrape profile pages. Do not guess private emails. Respect opt out. |
| 6 | LinkedIn search | User runs in their own account. Claude writes the strings and processes pasted results | Medium | Good for professional roles | Never automate. Follow the platform terms and limits. Message by hand. |
| 7 | Job board candidate search (Indeed, Naukri and similar) | User runs it in their own paid account. Claude writes the strings, processes exports | Medium | Good volume for common roles | Use only the export the platform allows. Contact within the platform's rules. |
| 8 | GitHub and code sites | Claude can run web search for public pages. User opens and reads profiles | Medium | Strong for engineers who publish work | Public profile data only. Do not harvest emails. Contact via a public contact option. |
| 9 | Portfolios (design, writing, video, photography) | Claude searches public portfolio sites. User reviews | Medium | Strong, you can see the real work | Respect copyright. Ask before using anyone's work. Judge the work, not the person's looks or name. |
| 10 | Communities (forums, Slack and Discord groups, subreddits, trade groups) | User posts or joins. Claude writes the post and the intro | Medium | High fit if the group matches the craft | Read each group's rules first. Many ban job posts or require a thread. Do not spam. |
| 11 | Universities, colleges, training providers | User contacts. Claude drafts the email | Low to medium | Good for entry roles and internships | Follow their process. Fair pay for interns. Check local rules for trainees (doc 12, 14). |
| 12 | Alumni of competitors and similar businesses | User identifies. Claude writes strings for public search and drafts a respectful note | Medium | High skill, may be hard to move | Do not ask anyone to break a contract or share secrets. Check non solicitation and non compete terms with a lawyer if relevant. |
| 13 | Freelancer marketplaces | User posts or browses in their own account. Claude writes the brief | Low | Good for tests and projects, can lead to hires | Follow the marketplace rules on taking people off the platform. |
| 14 | Events, meetups, local clubs | User attends. Claude prepares a short pitch and a follow up note | Medium | High trust, small numbers | Only collect contact details with consent. |
| 15 | Your own audience (email list, social posts, customers) | User posts. Claude writes it | Low | Often high fit and loyal | Do not email customers about jobs unless consent covers it. |
| 16 | Past applicants and silver medalists | Claude searches the user's own `hiring/` folders | Low | Often the best first stop | Only if they agreed to be kept (doc 03, 12). |
| 17 | Recruiters and agencies | User chooses and manages | Low | Varies widely | Get fee terms in writing (doc 02). |
| 18 | Local, offline places (shop windows, trade schools, community boards, local radio or paper) | User | Low | Good for local, hands on, shift work | Include a QR or short link that goes to your form. |

## How each type of channel works

### Inbound (1, 2, 3, 13, 15, 18): people come to you
Quality here depends on the post (doc 07) and the form. A clear pay range, a specific mission and honest hours bring fewer but better applicants.
Claude writes a post per platform from `templates/job-posts/` and checks it with `python3 tools/bias_check.py`. The user posts it.

### Outbound (5, 6, 7, 8, 9, 12, 14): you go to people
Outbound takes more effort but reaches people who are not looking. Build a list of prospects in `hiring/<role>/prospects.csv` with `python3 tools/prospects.py`.
Minimal data only: a public URL, a work related fit note, the source, and the date found. No private emails guessed or scraped.
Respect opt out: a person who says stop is marked and never contacted again.

### Warm (4, 10, 11, 14, 16): trust and context
Warm channels have the best acceptance, but also the biggest bias risk because they repeat what you already know. Use the same scorecard and blind first look (doc 08).

## Search strings and what Claude produces

`python3 tools/make_search_strings.py templates/scorecards/<role>.json --location "City"` prints markdown with who runs each string:

- **google_xray:** Claude runs through web search, reading public snippets only.
- **linkedin_search, indeed_search, naukri and wellfound strings:** the user pastes them in their own account.
- **github:** qualifiers (language, location, topics) that Claude may run through web search, not through a scrape of the site.
- **community prompts:** short posts for groups.
- **what not to do:** reminders (no private data, no automation).

Boolean strings come from scorecard keywords with synonyms. Keep them simple. Start broad, read 10 results, then tighten. Do not search on protected traits or proxies (age, gender, nationality, photo, name). The tool refuses obvious ones.

## Prospect and import flow

1. User exports or pastes results into `hiring/<role>/inbox/` (CSV, text, or saved pages they chose).
2. `python3 tools/prospects.py import --role <role> hiring/<role>/inbox/<file>` adds rows, dedupes by public URL and by name plus place, refuses private emails by default.
3. Claude adds a short work related fit note for each (what in the public work matches a criterion), never a note about looks, age or background.
4. `python3 tools/prospects.py mark --role <role> <id> <status>` as outreach goes (doc 09). Status moves: not_contacted, contacted, replied, interested, not_interested, stopped.
5. Candidates who apply become rows in the pipeline (`python3 tools/pipeline.py`).

## First week sourcing plan

Assume the scorecard, pay range and form are ready (docs 05 and 07). Adjust to your timeline.

| Day | Do | Who |
| --- | --- | --- |
| 1 | Confirm the scorecard, pay, location, start date. Run `new_role.py`. Pick 3 channels to start: one inbound, one warm, one outbound | Owner and Claude |
| 2 | Write the post and the form. Post on your careers page and the main board. Publish referral ask to staff and friends | Claude writes, owner posts |
| 3 | Generate search strings. Run the Google X-ray ones. Owner runs the LinkedIn or board searches and drops results in `inbox/` | Claude and owner |
| 4 | Import results, build 20 to 30 prospects with fit notes, rank them | Claude |
| 5 | Owner reviews the ranked list and approves the first outreach batch. Claude drafts the messages. Owner sends by hand | Owner |
| 6 | Post to one community or niche board. Send the college or training provider note | Owner |
| 7 | Run `pipeline.py weekly`. Count applicants, prospects, replies. Compare with the funnel plan (doc 01). Decide what to add next week | Owner and Claude |

If after a week the numbers are far below plan, widen the channels before you lower the bar. Check pay and the post first (they are the usual cause).

## Do this

1. Start with warm and inbound channels (they are cheap), then add outbound where the pool is small.
2. Use at least 3 channels at once. One channel hides weaknesses.
3. Write the post and the form for the channel (doc 07). A good post on a weak channel beats a bad post on a strong one.
4. Keep a prospects file and a pipeline file from day one.
5. Track source for every candidate so you learn which channel gives hires, not just applicants.
6. Review source quality at week 3: stop channels with many applicants and no finalists, double up on channels that produce finalists.
7. Respect every person's data and every platform's rules. When in doubt, do less and ask.

## Common mistakes

- Asking Claude to log in to LinkedIn or a board and "just pull profiles". It will not, and your account can be restricted.
- Guessing or scraping private emails.
- Sending the same copy and paste message to 200 people.
- One channel only, usually the biggest board.
- Counting applicants as success. Count finalists and hires per channel.
- Sourcing only from the same kind of background and calling it "fit".
- Posting in a community that bans job posts.
- Forgetting to remove people who asked to stop.
- Contacting a person's current employer or asking them to share confidential information.

## Numbers

| Item | Starting assumption | Replace with |
| --- | --- | --- |
| Prospects contacted per reply | 10 contacted for each reply (example) | Your reply rate from week 1 |
| Applicant to shortlist rate | 0.15 | Your own pipeline data (`--actual`) |
| Channels in week 1 | 3 | Your capacity |
| Hours per week on sourcing | 4 to 6 | Your calendar |

Use `python3 tools/funnel_calculator.py --hires N` to see how many prospects or applicants you need. The estimate is a planning guide, not a promise.

## Ask the owner

1. Where do the best people for this role usually spend time? (Default: Claude proposes 3 channels from the scorecard.)
2. Do you have a LinkedIn or board account you can use? (Default: you run the searches, Claude writes the strings.)
3. Who on the team could give 3 referral names this week? (Default: ask all staff.)
4. Do you have past applicants or silver medalists who agreed to be kept? (Default: no, start fresh.)
5. Are there places you must not post, or companies you must not approach? (Default: none known.)
