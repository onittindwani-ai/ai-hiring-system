# LinkedIn InMail or direct message

- **Use when:** The person accepted your connection, or you are messaging through InMail for a role that suits them.
- **Who sends:** The owner or hiring manager, by hand.
- **Channel:** LinkedIn message
- **Length limit:** About 600 characters is a good target (about 90 words). Keep it short enough to read on a phone.

## Message

Subject: {{role_title}} at {{company_name}}

Hi {{candidate_first_name}},

I'm {{recruiter_name}} from {{company_name}}. {{specific_detail}}

We're looking for a {{role_title}}. The work is {{one_line_role_summary}}, and the pay range is {{pay_range}}.

If that sounds interesting, you can pick a time for a 20 minute call here: {{booking_link}}. If it's not for you, no problem at all, and a quick "no thanks" helps me too.

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
- Put the pay range in. People should not have to ask for it. If it is not decided yet, do not send the message yet.

## Variables used

`{{role_title}}`, `{{company_name}}`, `{{candidate_first_name}}`, `{{recruiter_name}}`, `{{specific_detail}}`, `{{one_line_role_summary}}`, `{{pay_range}}`, `{{booking_link}}`
