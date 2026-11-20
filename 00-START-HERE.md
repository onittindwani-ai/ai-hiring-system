# 00. Start here: your first 10 minutes

You do not need to know anything about recruiting. Claude runs the funnel and asks you only what it cannot find out itself.

## The 4 steps

1. **Install Claude Code** and open it inside this folder (see https://code.claude.com/docs). You need a paid Claude plan. Python 3.9 or newer must be on your computer (`python3 --version`).
2. **Paste the prompt** from `02-QUICK-START-PROMPT.md` (or just type `/hire-start`).
3. **Answer the first question**: which browser do you use. Claude tells you what to install, honestly, and what works in your browser.
4. **Give three things**: your company name, your website and any other page about you. Claude researches you first, tells you what it understood in 6 lines, and gives at most 4 real hiring moves. You pick one, or say who you want to hire.

From there Claude plans the hire (budget, how many people, timeline), writes the scorecard and the job posts, helps you find prospects, scores applicants with evidence, drafts every message for your approval, builds interview kits, and tells you every week where the funnel leaks.

## What you do and what Claude does

| You | Claude |
| --- | --- |
| Say yes, press Post and Send, sign in to your own accounts, decide every hire | Research, plan, write, score, draft, track, explain |
| Run searches on LinkedIn and Indeed in your own account and paste the results | Writes the search strings, reads your results, ranks and drafts |
| Approve each batch of messages | Never sends anything without your yes |

## See it work in 60 seconds, no setup

```
python3 examples/01_full_demo.py
```

This runs the whole funnel on a fake company and 20 fake candidates, offline, with no key (the folder holds 60 fake candidates in all, across 3 roles). It shows the plan, the scorecard check, the search strings, the scores, the shortlist and the first messages.

## Optional: Jev

A very fast scoring model that makes big batches quicker. Not needed. Claude offers it once, kindly, and moves on if you say no. See `docs/JEV-OPTIONAL.md`.

## Honest limits

Claude never drives LinkedIn, Indeed or other job boards (their rules do not allow bots), it never posts or sends for you, and a person decides every no and every offer. Read `docs/HONEST-LIMITS.md` once.
