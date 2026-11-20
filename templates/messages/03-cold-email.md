# Cold email

- **Use when:** You found a public work email or contact page that the person published for work contact, and you think they could fit the role.
- **Who sends:** The owner or hiring manager, by hand, from a company email address.
- **Channel:** Email
- **Length limit:** Subject under 60 characters. Body about 100 to 130 words.

## Message

Subject: A {{role_title}} role at {{company_name}}

Hi {{candidate_first_name}},

I'm {{recruiter_name}} at {{company_name}}. {{specific_detail}}

We're hiring a {{role_title}}. In the first 90 days the person would {{first_outcome}}. The pay range is {{pay_range}} and the start date is around {{start_date}}.

Would you be open to a short call? You can choose a time here: {{booking_link}}. If you know someone who might fit better, I'd be glad to hear about them.

Thanks for reading,
{{recruiter_name}}
{{company_name}}

Reply STOP and I won't message you again.

## Rules

- You (the owner) approve the exact text and the list before anything is sent. Claude only drafts it.
- Use `{{specific_detail}}` only for a real, verified fact from the person's public profile or work. If you have no real detail, delete that sentence. Never invent or guess one.
- Say plainly who you are, who the company is and why you are writing. Do not pretend to know the person.
- Do not mention age, gender, nationality, photo, family or any personal trait. Talk about their work only.
- Never promise a job. Say it is a conversation.
- Check the opt out list first. Anyone who replied STOP or asked not to be contacted gets nothing more, ever.
- You send it by hand from your own account. Claude does not log in to LinkedIn or any job board for you.
- Only use a work contact the person made public for work. Never guess, buy or scrape email addresses.
- Use the company's real name, address and a way to reach you in your email signature.

## Variables used

`{{role_title}}`, `{{company_name}}`, `{{candidate_first_name}}`, `{{recruiter_name}}`, `{{specific_detail}}`, `{{first_outcome}}`, `{{pay_range}}`, `{{start_date}}`, `{{booking_link}}`
