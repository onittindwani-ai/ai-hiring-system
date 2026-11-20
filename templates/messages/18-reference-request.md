# Reference request

- **Use when:** The candidate gave a reference and agreed that you may contact them.
- **Who sends:** The hiring manager or owner.
- **Channel:** Email or phone
- **Length limit:** Under 120 words.

## Message

Subject: Reference for {{candidate_full_name}}

Hi {{referee_first_name}},

{{candidate_full_name}} gave your name as a reference for a {{role_title}} role at {{company_name}} and agreed that we may contact you. Thank you for considering it.

Would you have 15 minutes this week for a call, or would you prefer to answer five short questions by email? You can choose here: {{booking_link}}.

We will ask about the work you saw them do, and we will keep what you tell us confidential, shared only with the people making the hiring decision. You can decline any question.

Thank you,
{{recruiter_name}}

## Rules

- You (the owner) approve the exact text before it is sent. Claude only drafts it.
- Never invent a personal detail. Use `{{specific_detail}}` only for a real fact the person gave you in their application or in the conversation.
- Never promise a job unless this is the offer message and the offer is approved and real.
- No dashes, no hype, no pressure. Plain, warm and short.
- Get the candidate's permission before contacting anyone. Never contact a current employer without the candidate saying yes.
- Ask every referee for the same role the same job related questions (see `templates/interviews/reference-check.md`).
- Use only what is true and job related. Never ask about health, family, age or other protected topics.

## Variables used

`{{referee_first_name}}`, `{{candidate_full_name}}`, `{{role_title}}`, `{{company_name}}`, `{{booking_link}}`, `{{recruiter_name}}`
