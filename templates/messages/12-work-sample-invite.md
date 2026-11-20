# Work sample invite

- **Use when:** The candidate reached the work sample step on the scorecard.
- **Who sends:** The hiring manager or owner.
- **Channel:** Email
- **Length limit:** Under 160 words.

## Message

Subject: A short task for the {{role_title}} role

Hi {{candidate_first_name}},

The next step is a short task that looks like real work for this role. It should take about {{work_sample_hours}} hours, and we ask you to stop at that time even if it is not perfect.

The task: {{work_sample_brief}}

Send your work to {{submission_address}} by {{deadline}}. You can use the tools you normally use. If you use AI tools, just tell us how.

We will read it the same way as everyone else, using a short checklist we can share with you. If this is not a good time, tell us and we will find another day. {{work_sample_pay_note}}

Thank you,
{{recruiter_name}}

## Rules

- You (the owner) approve the exact text before it is sent. Claude only drafts it.
- Never invent a personal detail. Use `{{specific_detail}}` only for a real fact the person gave you in their application or in the conversation.
- Never promise a job unless this is the offer message and the offer is approved and real.
- No dashes, no hype, no pressure. Plain, warm and short.
- Keep the task real, short and about the job. Never ask for work the company will use for free in its business. If the task is long, pay for the time (`{{work_sample_pay_note}}` says what you pay, or says that the task is fictional and short).
- Give the same task, time and scoring to every candidate for the role.
- Offer a different format or time to anyone who asks.

## Variables used

`{{role_title}}`, `{{candidate_first_name}}`, `{{work_sample_hours}}`, `{{work_sample_brief}}`, `{{submission_address}}`, `{{deadline}}`, `{{work_sample_pay_note}}`, `{{recruiter_name}}`
