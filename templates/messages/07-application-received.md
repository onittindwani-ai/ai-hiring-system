# Application received

- **Use when:** Someone applied (form, email or board) and you want them to know it arrived.
- **Who sends:** Sent automatically by your form tool or by you, after you approve the text once.
- **Channel:** Email
- **Length limit:** Subject under 60 characters. Body under 90 words.

## Message

Subject: We got your application for {{role_title}}

Hi {{candidate_first_name}},

Thank you for applying for the {{role_title}} role at {{company_name}}. We have your application.

What happens next: we read every application ourselves and look at the work related answers, not at personal details. You will hear from us by {{reply_by_date}} either way.

If you need any adjustment to take part in the process, tell us at {{contact_email}} and we will help.

{{recruiter_name}}

## Rules

- You (the owner) approve the exact text before it is sent. Claude only drafts it.
- Never invent a personal detail. Use `{{specific_detail}}` only for a real fact the person gave you in their application or in the conversation.
- Never promise a job unless this is the offer message and the offer is approved and real.
- No dashes, no hype, no pressure. Plain, warm and short.
- Only promise a date you can keep. If the date slips, send a short update before it passes.
- Say how long and how many steps the process has if you know. People wait better when they know.

## Variables used

`{{role_title}}`, `{{candidate_first_name}}`, `{{company_name}}`, `{{reply_by_date}}`, `{{contact_email}}`, `{{recruiter_name}}`
