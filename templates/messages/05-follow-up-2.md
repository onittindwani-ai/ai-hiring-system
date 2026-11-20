# Second and last follow up (7 to 10 days after the first)

- **Use when:** There was still no reply after follow up 1 and the person has not opted out.
- **Who sends:** The owner or hiring manager, by hand.
- **Channel:** Same channel as the first message
- **Length limit:** Under 50 words.

## Message

Hi {{candidate_first_name}},

This is my last note about the {{role_title}} role at {{company_name}}. If you want to talk, the link is here: {{booking_link}}. Either way, I wish you well.

{{recruiter_name}}

Reply STOP and I won't message you again.

## Rules

- You (the owner) approve the exact text and the list before anything is sent. Claude only drafts it.
- Use `{{specific_detail}}` only for a real, verified fact from the person's public profile or work. If you have no real detail, delete that sentence. Never invent or guess one.
- Say plainly who you are, who the company is and why you are writing. Do not pretend to know the person.
- Do not mention age, gender, nationality, photo, family or any personal trait. Talk about their work only.
- Never promise a job. Say it is a conversation.
- Check the opt out list first. Anyone who replied STOP or asked not to be contacted gets nothing more, ever.
- You send it by hand from your own account. Claude does not log in to LinkedIn or any job board for you.
- This is the last message. After it, mark the person as `not_interested` or `no reply` in the prospects file and do not contact them again for this role.
- No guilt, no countdown, no pretending the role will close.

## Variables used

`{{candidate_first_name}}`, `{{role_title}}`, `{{company_name}}`, `{{booking_link}}`, `{{recruiter_name}}`
