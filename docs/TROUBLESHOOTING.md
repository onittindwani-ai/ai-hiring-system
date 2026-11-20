# Troubleshooting

| What you see | What to do |
| --- | --- |
| Claude does not offer the setup | Say `/hire-start` or "start hiring setup". Check that you opened this folder in Claude Code. |
| `python3: command not found` | Install Python 3.9 or newer from python.org, then run `python3 --version`. |
| Claude in Chrome does not connect | Run `/chrome` in Claude Code. You need a paid Claude plan and a `/login` with that account. Chrome is the supported browser; Edge works per the Claude Code docs. Otherwise use manual mode. |
| Brave or another browser does not work | Anthropic lists only Chrome as supported. Use Chrome for this, or manual mode. |
| A login or CAPTCHA appears | Handle it yourself, then tell Claude to continue. Claude never types passwords. |
| `No API key found` from Jev | Jev is optional. To use it set the key in your own terminal (see JEV-OPTIONAL.md). Or continue with Claude scoring. |
| Jev says 401 | The key is wrong or deleted: make a new one at console.typesafe.ai/keys. |
| Jev says 429 or 529 | Rate limit or overload. The tool retries; wait a minute and run again. |
| Jev: cannot create a key | The console may need credit first. Add a few dollars in Billing. |
| Scores look wrong | Run `python3 tools/evaluate.py` on the sample data to see how the engine does, then check the scorecard keywords and levels. Calibrate on 5 candidates first. |
| A candidate shows `review` | A flag fired (injection text, low confidence, or an unknown gate). A person looks at it. |
| Form script fails in Google | File upload questions cannot be created by script. Use a link question instead. |
| Tests fail | Run `python3 -m unittest discover -s tests` and read the first failure. |
