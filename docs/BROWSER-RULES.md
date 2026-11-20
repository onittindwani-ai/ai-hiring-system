# Browser rules: what Claude may and may not open

Plain version: Claude uses your browser only for YOUR own tools, only after telling you what it will open, and only after you say yes. Claude never opens LinkedIn, Indeed, Naukri or any job board, and never types a password.

## Why

LinkedIn's help pages (checked on 2026-11-20) say the site does not permit third party software, including bots and browser extensions, that scrape, modify or automate activity, and that accounts can be restricted. Other job boards have similar terms. A recruiter tool that breaks those terms puts your account and your hiring at risk, so this system does not do it. That is a design choice, not a missing feature.

## Allowed (with your yes, in your own signed in browser)

| Task | Where |
| --- | --- |
| Create the application form and the answers Sheet | Google Forms, Tally, Google Sheets |
| Put interviews in your calendar | Google Calendar or your own calendar app |
| Create email drafts (you press send) | Gmail or Outlook on the web |
| Read your own company website, your careers page | your site |
| Read public web pages found by search | public pages only |

## Not allowed

| Task | What happens instead |
| --- | --- |
| Searching or reading profiles on LinkedIn | You run the search in your own account. Claude writes the search string and reads what you paste or export. |
| Searching Indeed, Naukri or similar candidate databases | Same: you run it, Claude helps with the string and the results. |
| Posting a job on a board | Claude writes the post, you paste it and press Post. |
| Sending connection requests or messages on LinkedIn | Claude writes the text, you send it. |
| Logging in for you, getting past a CAPTCHA | You do it. Claude waits. |

## Checks before any browser step

1. Say what you will open and why, in one line.
2. Wait for a yes.
3. If a login or CAPTCHA appears, stop and let the owner handle it.
4. Close what you opened. Report what you did.

## If you use Safari or Firefox

There is no extension. Claude gives click by click steps (or an Apps Script from `tools/make_form_script.py`) and you do the clicks. Everything else works the same.
