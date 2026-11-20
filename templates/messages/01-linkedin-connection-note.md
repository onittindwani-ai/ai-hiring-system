# LinkedIn connection note

- **Use when:** You want to connect with a person you found by search before you message them.
- **Who sends:** The owner or hiring manager, by hand, from their own LinkedIn account.
- **Channel:** LinkedIn connection request note
- **Length limit:** 300 characters for the whole note, including the STOP line (check LinkedIn's current limit, it can change). Drop the `{{specific_detail}}` sentence if it makes the text too long.

## Message

Hi {{candidate_first_name}}, I'm {{recruiter_name}} at {{company_name}}. {{specific_detail}} We're hiring a {{role_title}} and I'd value a short chat, no pressure. Reply STOP and I won't message you again.

## Rules

- You (the owner) approve the exact text and the list before anything is sent. Claude only drafts it.
- Use `{{specific_detail}}` only for a real, verified fact from the person's public profile or work. If you have no real detail, delete that sentence. Never invent or guess one.
- Say plainly who you are, who the company is and why you are writing. Do not pretend to know the person.
- Do not mention age, gender, nationality, photo, family or any personal trait. Talk about their work only.
- Never promise a job. Say it is a conversation.
- Check the opt out list first. Anyone who replied STOP or asked not to be contacted gets nothing more, ever.
- You send it by hand from your own account. Claude does not log in to LinkedIn or any job board for you.
- After you fill the placeholders, count the characters. If it is over 300, shorten the detail sentence first, never the STOP line.

## Variables used

`{{candidate_first_name}}`, `{{recruiter_name}}`, `{{company_name}}`, `{{specific_detail}}`, `{{role_title}}`
