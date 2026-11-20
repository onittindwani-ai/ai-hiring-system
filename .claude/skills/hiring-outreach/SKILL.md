---
name: hiring-outreach
description: Drafts honest outreach, follow ups, invites, referral asks, declines and offers from the templates, held for approval; the user sends them. Use when the user says write messages, reach out, email these people, follow up, decline, invite to interview, or send the offer.
---

# Hiring outreach

Read `docs/knowledge/09-OUTREACH-AND-FOLLOW-UP.md` and the matching file in `templates/messages/` (20 templates).

## Steps

1. Pick the template for the moment: cold outreach (connection note, InMail, email), follow ups, referral ask, application received, screening invite, interview invite, reminder, reschedule, work sample, decline, offer, reference request, welcome, keep warm.
2. Fill the variables from real data only. `{{specific_detail}}` must be a fact you can point to (a public project, a post, a talk the person published). If you cannot verify a detail, leave it out. Never flatter with an invented detail. Never promise a job.
3. Render with `python3 tools/render_message.py <template> --vars vars.json --out hiring/<role>/drafts/<name>.md`, then check with `python3 tools/message_check.py <file> --kind cold|candidate`. Fix every flag (placeholders, length, missing STOP line, spam words).
4. Show the owner the first 2 drafts in full and list the rest by name. Ask one question: "Send these?" per batch. Nothing leaves without a yes.
5. **The owner sends.** Email: if an official Gmail or Outlook connector is installed and the owner says "send these", create drafts in their drafts folder and let them press send, or send only after their explicit yes for that batch. LinkedIn: give the text and the person's public URL, the owner pastes and presses send in their own account. Mark `contacted` with `python3 tools/prospects.py mark` or `python3 tools/pipeline.py move`.
6. **Cadence**: first touch, a follow up after 3 to 4 days, a last short follow up after another week, then stop. Anyone who says stop is marked `stopped` and never contacted again (`prospects.py mark --role <role> <id> stopped`).
7. Replies: read what the person wrote, classify it (interested, question, not now, stop), draft the answer, hold for the owner's yes. A "not now" is kept warm, not chased.

## Rules

Cold messages are short, specific, honest about who is writing and why, with the line `Reply STOP and I won't message you again.` Candidate messages are kind and clear, with a next step and a time. Declines are sent in good time and never leave anyone waiting. No dashes in messages. Do not send anything to anyone who has not been approved by the owner.
