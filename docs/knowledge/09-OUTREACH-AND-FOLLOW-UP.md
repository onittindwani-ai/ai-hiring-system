# 09. Outreach and follow up

## Purpose
Reach people who might be a great fit, honestly and briefly, and treat every person well whether they say yes or no.
Claude writes the messages. The owner sends them by hand from their own accounts.

## Ground rules
- Claude never sends, posts or messages anyone. It writes drafts and checks them (`tools/message_check.py`). You send.
- Claude never drives LinkedIn, Indeed, Naukri or similar sites. You search and message in your own account. See `docs/BROWSER-RULES.md`.
- Only real facts about a person go in a message. If Claude does not have a verified detail, the message is shorter and says nothing personal. A true plain message beats a fake warm one.
- Everyone can say stop. One reply of "no" or "stop" ends all contact, and it is recorded.

## Who does what
| Step | Claude | You |
| --- | --- | --- |
| Find public profiles | runs public web searches, lists them with a fit note | runs searches in your own LinkedIn or job board account |
| Write messages | drafts, checks length, flags risky words | reads, edits, approves |
| Send | never | sends by hand from your own account |
| Track | updates `prospects.csv` from what you tell it | tells it who replied and what they said |
| Reply | drafts a reply | reads and sends |

## Do this
1. Build the prospect list from public information only: public profile pages, portfolios, repos, community posts, Google results. Record the public URL and a one line, job related reason for the fit (`tools/prospects.py`). Do not guess private emails. Do not scrape.
2. For each message, fill `{{specific_detail}}` only with something you or Claude actually saw and can point to (for example "your open source invoice tool", "your talk on route planning"). If you cannot point to it, leave the line out.
3. Use the shape that works (below). Draft it, run `tools/message_check.py`, read it aloud once, then send by hand.
4. Log every contact in `prospects.csv` with `contact_status` and the date. A person who replied "not interested" or "stop" is `not_interested` or `stopped` and is never contacted for this role again.
5. Follow up on a schedule (cadence table). Stop after the last step.
6. Reply to every human reply within 1 working day. Claude drafts the reply, you send it.
7. Ask for referrals from everyone who says no, in one friendly line.
8. Every week, count: sent, replied, interested, booked. Fix the weakest step (doc 01 for the funnel math).

## The message shape that works
Four short parts, 60 to 110 words for email, under 300 characters for a LinkedIn connection note.
1. Who you are and why this person (one true detail, or none).
2. What the job is, in one plain sentence, with the pay range if you can share it.
3. What you ask for: a 15 minute call, or "reply yes and I send details". One ask only.
4. An easy way out: "If not for you, no problem. Reply STOP and I won't message again."
Subject lines (email): plain and short, under 60 characters. "A {{role_title}} role at {{company_name}}" is fine. No tricks, no fake "Re:", no all caps.
Example (made up, fictional company):
> Hi Priya, I'm Sam, I run operations at Northlight Home Services, a home repair and cleaning business in two cities. I'm hiring a bookkeeper (part time, pay range in the post). I found your public write up on month end checklists and it matches what we need. Would a 15 minute call this week suit you? If this is not for you, no problem, reply STOP and I won't write again.
Note: the detail about the write up is only allowed if it was real. If it was not seen, delete that sentence.

## What honest personalization means
- Allowed: a public project, article, talk, product, a shared community, a job title and company from a public page, a mutual introduction you really have.
- Not allowed: "I loved your recent post" with no post, invented compliments, claiming you know their work when you do not, pretending to be a friend or a recruiter from another company, fake urgency ("only 2 spots left"), made up salary.
- Never mention anything private or sensitive (health, family, age, where they live beyond what the job needs, a layoff they did not announce).
- Never use a detail that hints at a protected trait to choose who to contact. Pick people for the work they show.

## Channels
| Channel | Who sends | Notes |
| --- | --- | --- |
| LinkedIn message | you, by hand, in your own account | Claude writes the note. Respect the site's limits. No automation tools. |
| Email to a public work address | you, from your own email | Only addresses the person published for work contact. Include the opt out line. |
| Community post or DM | you, by hand | Read the community rules first. Post the job openly instead of mass DMs. |
| Referral request to your network | you | Ask for a name and a reason, not a favor. |
| SMS | you, only if the person gave you their number for this purpose | Limit 160 characters. Rarely right for a first contact. |

## Cadence (starting assumption, replace with your own data)
| Step | When | What |
| --- | --- | --- |
| 1 first message | day 0 | the shape above |
| 2 short follow up | day 4 or 5 | one line, add one new useful fact (the pay range, a deadline), not "just bumping" |
| 3 last note | day 10 | polite close: "I'll leave it here. If it's ever interesting, my door is open." |
After step 3, stop. No fourth message. No new channel to the same person for the same role.
Do not send at night or on weekends in the person's time zone. Pick 9 to 11 in their morning (starting assumption).

## Reply handling
| Reply | What to do |
| --- | --- |
| "Interested" | Thank them. Send 2 or 3 time options or a booking link, plus the job details and pay range. Mark `interested`. |
| "Tell me more" | Send the job post, pay range, team size, how the process works and how long it takes. Do not oversell. |
| "Not now, maybe later" | Thank them. Ask if you may keep their public details for 6 months and write once. Record the answer. |
| "No thanks" | Thank them. Ask for a referral in one line. Mark `not_interested`. |
| "Stop" or any form of "do not contact" | Stop at once. Mark `stopped` and `opt_out` yes. Reply once: "Understood, I won't write again." |
| Asks about pay | Answer with the real range. If you cannot say, tell them when you can. |
| Angry or rude | Apologize briefly, stop contact, mark `stopped`. Do not argue. |
| Questions about how you found them | Tell the truth (public page and which one). Offer to delete their record if they want. |
| A question about law or visas | Do not guess. Say you will check and come back, or point to the job post's stated rules. |

## Referral asks
- Ask your team, past colleagues, vendors, customers who like you, and every person who says no.
- Make it easy: "Do you know one person who is excellent at {{outcome}}? I'll write them a short note and say you suggested it, only if you say that's fine."
- Never use a referral's name without their yes.
- Thank the referrer whatever happens. If you pay a referral bonus, write the rule down in advance and apply it the same for everyone.

## Candidate experience (this is outreach too)
- Confirm every application in 1 working day (an auto reply is fine if honest about timing).
- Tell people the process and the dates: stages, who they meet, how long each takes, when they will hear.
- Never leave a person in silence. A "no" within a promised window is respectful. Silence is the thing candidates remember.
- Keep scheduling easy: offer time zones clearly, allow rescheduling once without drama.
- Share the pay range early. It saves time on both sides.
- Offer reasonable accommodations in every invitation ("tell us if you need anything to make the interview work for you").

## The decline message
A good decline is fast, kind, specific enough to feel real, and short.
1. Thank them for the time they gave.
2. Say it plainly: "we're not moving forward".
3. One honest, job related reason in a few words, or none. Never a reason about personal traits. Never an invented reason.
4. Offer something real if true: keep their details for 6 months, a pointer to another role, or one line of feedback if you promised it.
5. Wish them well.
Example (made up):
> Hi Marcus, thank you for the time you gave us, including the work sample. We've decided to move ahead with another candidate whose experience with month end close was closer to what this role needs right now. We enjoyed meeting you, and with your OK we'd like to keep your details for 6 months in case something fits. Good luck with the search.
A person decides every decline. Claude drafts it, you read and send.

## Common mistakes
- A long first message that tells the whole company story.
- Fake personalization, which people spot in a second.
- Ten follow ups. Three is the limit.
- Sending to someone who said stop (even by mistake: check `opt_out` before every send).
- Hiding the pay range and the process.
- Mass messaging a community when a post would do.
- Using an AI tool to message from a job board account (breaks the site rules and can get the account blocked).
- Ghosting candidates after an interview.
- Using a referral as a way to skip the scorecard.

## Numbers
- Connection note: 300 characters or fewer. Email subject: 60 or fewer. SMS: 160 or fewer. (platform and good practice limits; `tools/message_check.py` checks them. Check the platform for changes.)
- Cadence of 3 touches over 10 days (starting assumption).
- Reply rate for cold outreach: start at 10 to 20 percent as a planning guess for a warm, specific note, and 3 to 8 percent for a generic one (starting assumptions, replace with your own data after your first 30 sends).
- Prospects to contact = applicants needed / prospect_to_applicant rate. `tools/funnel_calculator.py` does it for you with a starting assumption of 0.10 (10 contacted for each person who applies), prints it, and uses your own rate once you pass `--actual`. A reply is not yet an application, so your reply rate will be higher than that number.

## Ask the owner
1. Which account will send messages (LinkedIn, email), and what name do you want at the bottom? Default: your own, with your real title.
2. Can we share the pay range in the first message? Default: yes, the range from the job post.
3. Who handles replies, and how fast? Default: you, within 1 working day.
4. Do you pay a referral bonus? Default: no, unless you write the amount and the rule down.
5. How long do you keep a person's details after a no? Default: 6 months with their OK, otherwise delete at the end of the search.
