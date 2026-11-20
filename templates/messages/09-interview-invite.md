# Interview invite

- **Use when:** The candidate passed screening and you want to book the interview.
- **Who sends:** The hiring manager or owner.
- **Channel:** Email
- **Length limit:** Under 130 words.

## Message

Subject: Interview for {{role_title}}

Hi {{candidate_first_name}},

We'd like to invite you to an interview for the {{role_title}} role.

- When: {{interview_time}} (please tell us if another time works better)
- How long: {{interview_length}} minutes
- Where: {{interview_format}}
- Who: {{interviewer_names}}

We will ask about real situations from your work, and the same questions go to every candidate for this role. You do not need to prepare anything special. If you want, you can look at {{company_name}}'s website first.

If you need anything to make the interview easier (a different time, a written version, more time), reply and we will arrange it.

{{recruiter_name}}

## Rules

- You (the owner) approve the exact text before it is sent. Claude only drafts it.
- Never invent a personal detail. Use `{{specific_detail}}` only for a real fact the person gave you in their application or in the conversation.
- Never promise a job unless this is the offer message and the offer is approved and real.
- No dashes, no hype, no pressure. Plain, warm and short.
- List exactly who will be there, how long it takes and how to join. Test the video link first.
- Use the same structured questions for everyone for this role (see `templates/interviews/interview-guide.md`).

## Variables used

`{{role_title}}`, `{{candidate_first_name}}`, `{{interview_time}}`, `{{interview_length}}`, `{{interview_format}}`, `{{interviewer_names}}`, `{{company_name}}`, `{{recruiter_name}}`
