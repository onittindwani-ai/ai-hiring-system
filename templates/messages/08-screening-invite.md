# Screening invite

- **Use when:** The candidate looks like a fit on the scorecard and you want a short first call or a few written questions.
- **Who sends:** The owner or hiring manager, after reviewing the shortlist.
- **Channel:** Email
- **Length limit:** Under 110 words.

## Message

Subject: Next step for {{role_title}} at {{company_name}}

Hi {{candidate_first_name}},

Thanks for applying. Your answers about {{specific_detail}} stood out to us, so we'd like to talk.

The next step is a {{call_length}} minute call about the work itself. Pick a time that suits you here: {{booking_link}}. If you prefer to answer a few questions in writing instead, reply and say so.

For reference, the pay range for this role is {{pay_range}}, so we are both clear from the start.

Looking forward to it,
{{recruiter_name}}

## Rules

- You (the owner) approve the exact text before it is sent. Claude only drafts it.
- Never invent a personal detail. Use `{{specific_detail}}` only for a real fact the person gave you in their application or in the conversation.
- Never promise a job unless this is the offer message and the offer is approved and real.
- No dashes, no hype, no pressure. Plain, warm and short.
- `{{specific_detail}}` must be something the person wrote or did, found in their application. Re read it before sending.
- Offer a written option or a different time to anyone who needs it. Do not ask why.

## Variables used

`{{role_title}}`, `{{company_name}}`, `{{candidate_first_name}}`, `{{specific_detail}}`, `{{call_length}}`, `{{booking_link}}`, `{{pay_range}}`, `{{recruiter_name}}`
