# 01. Setup (5 minutes)

Written from the current docs on 2026-11-20. Screens and rules change, so look for the same words if a button moved.

## You need

- A computer with Python 3.9 or newer (`python3 --version`).
- Claude Code, and a paid Claude plan (Pro, Max, Ultra, Team or Enterprise).
- Optional: the Claude in Chrome extension, so Claude can build your application form and put interviews in your calendar. Without it everything still works in manual mode.

## Steps

1. Download or clone this folder, then open a terminal in it and run `claude` (Claude Code).
2. Run `python3 tools/check_setup.py`. It prints a plain readiness report and never shows a key.
3. Paste the prompt from `02-QUICK-START-PROMPT.md`, or type `/hire-start`.
4. Answer the browser question. What Claude will tell you:

| Your browser | What happens |
| --- | --- |
| Google Chrome | Install Claude in Chrome from https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn , then run `/chrome` in Claude Code to check the connection. Steps: https://code.claude.com/docs/en/chrome |
| Microsoft Edge | Claude Code's docs list Edge as working. Same link; Edge can usually add extensions from the Chrome Web Store. |
| Brave, Arc or another Chromium browser | It might connect (Claude Code's docs say so) but Anthropic's support page lists only Chrome. Chrome is the safe choice. |
| Safari or Firefox | No extension exists. Manual mode: Claude writes everything and gives click by click steps. |

5. Say yes to the browser rules: Claude uses the browser only for your own tools (Google Forms, Sheets, Calendar, email web app, your site), tells you what it will open, and never types a password. It never opens LinkedIn or job boards. Details: `docs/BROWSER-RULES.md`.
6. Optional: Jev. Claude asks once. See `docs/JEV-OPTIONAL.md`.

## Safety rules

- Never paste a key or password into the chat. Keys go in your own terminal.
- Real candidate files live in `hiring/`, which is git ignored. Never commit them.
- Nothing is posted, sent or rejected without your clear yes.

## If something goes wrong

See `docs/TROUBLESHOOTING.md`.
