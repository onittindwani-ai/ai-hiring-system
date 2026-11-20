---
name: hiring-start
description: First run of the AI Hiring System. Sets up the browser, researches the company from its name and website, confirms what it learned in a few lines, and suggests at most four real hiring moves. Use when config/profile.json is missing or the user says start, set up, or I want to hire. Not for scoring or writing posts.
---

# Hiring start

Goal: in about 5 minutes the user has a working setup and Claude understands their business. Keep every message short (see CLAUDE.md "How to talk").

## Step 0. Setup (skip if `config/profile.json` has `"setup_done": true`)

Run `python3 tools/check_setup.py` first and read it silently. Then send ONE question:

> Which browser do you use? 1) Google Chrome 2) Microsoft Edge 3) Brave, Arc or another Chromium browser 4) Safari or Firefox

Answer by choice, in 4 to 6 lines:

- **Chrome**: "Install Claude in Chrome: https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn . It needs a paid Claude plan (Pro, Max, Ultra, Team or Enterprise) and a Claude Code login with that account. Run `/chrome` in Claude Code to check or turn on the connection (steps: https://code.claude.com/docs/en/chrome). Tell me when it is done."
- **Edge**: same link. Say: Claude Code's docs list Edge as working, and Edge can usually add extensions from the Chrome Web Store.
- **Brave, Arc, other Chromium**: same link, but say plainly that Anthropic's support page lists only Chrome as supported while Claude Code's docs say other Chromium browsers may connect, so it might work and Chrome is the safe choice. Offer manual mode.
- **Safari or Firefox**: there is no extension for these. Use manual mode: Claude writes everything and gives click by click steps. Nothing is lost except the browser shortcuts.

Then say, in one short paragraph, how the browser is used: "With your OK I use it only for your own tools: Google Forms, Sheets, Calendar, your email and your company website. I never open LinkedIn, Indeed or other job boards, I never type passwords (you sign in), and I tell you what I will open before I open it." Ask for a yes. Save `browser`, `browser_mode` (extension or manual) and `browser_consent` in `config/profile.json` (copy `config/profile.example.json` first).

Then offer Jev once, in the friendly words from the `hiring-jev` skill (now, later, or skip). Record the answer in `config/profile.json` as `jev`: `now`, `later` or `declined`. If skip: say "All good, no problem" and move on. Never push.

Finally ask which email they use for candidates (Gmail, Outlook, other) and whether they have a booking link. Both optional, defaults: none. Set `"setup_done": true`.

## Step 1. The company (ask only three things)

> What is your company name, your website, and any other page about you (careers page, social page)?

Do not ask anything else yet. Research by yourself: read the website with your web fetch tool, search the web for public information. Never open LinkedIn pages. If they gave a LinkedIn link, ask them to paste the About text instead. Gather: what they sell and to whom, size hints, locations, how they sound, current openings, growth signals, tools they seem to use.

Reply in 6 lines or fewer: "This is what I understood: ...". Label guesses ("looks like", "probably"). Ask only "Is that right? Anything to fix?". Save the confirmed summary to `config/profile.json` (`company`) and `hiring/company.md`.

## Step 2. Suggestions (after they confirm)

Give 1 to 4 hiring moves, never more. Each must be a real, money making or money saving move that the research supports, one line each: the role, the evidence you saw, the likely effect (label it inference). Rank by money. If nothing is strong, say "Nothing stands out yet, tell me who you want to hire" and stop. Never list generic tips. No wall of text.

End with one next step: "Tell me which one (or your own) and I will plan it." Then use `hiring-plan`.

## If `config/profile.json` already exists

Show three lines: company, open roles in `hiring/`, what is waiting on them. Offer the next safe step.

## Never

Ask for a password, key or token. Open LinkedIn or a job board. Ask what the website already tells you. Dump a long list.
