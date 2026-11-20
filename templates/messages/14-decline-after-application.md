# Decline after application

- **Use when:** The person is not shortlisted now. A human owner decided this after reading the scores, not a tool.
- **Who sends:** The owner or hiring manager.
- **Channel:** Email
- **Length limit:** Under 90 words.

## Message

Subject: Your application for {{role_title}}

Hi {{candidate_first_name}},

Thank you for applying for the {{role_title}} role at {{company_name}} and for the time you spent on it.

We have decided to move forward with other applicants whose experience is closer to what this role needs right now. This is about fit for this one job, not a judgment of you.

We will keep your details only as long as we said in our notice and then delete them. If you would like them deleted sooner, reply to this email. We wish you well.

{{recruiter_name}}

## Rules

- You (the owner) approve the exact text before it is sent. Claude only drafts it.
- Never invent a personal detail. Use `{{specific_detail}}` only for a real fact the person gave you in their application or in the conversation.
- Never promise a job unless this is the offer message and the offer is approved and real.
- No dashes, no hype, no pressure. Plain, warm and short.
- A person made this decision. Never let a tool send a rejection by itself.
- Be kind and clear. Do not say 'we will keep your resume on file' unless you really will, and say for how long.
- Do not give a reason that touches a protected trait. If the person asks for feedback, give job related feedback only.

## Variables used

`{{role_title}}`, `{{candidate_first_name}}`, `{{company_name}}`, `{{recruiter_name}}`
