# How it works

## The funnel Claude runs

```
start -> plan -> scorecard -> post and form -> source -> screen -> outreach -> interview -> offer -> weekly review
```

| Step | Skill | What you get | You do |
| --- | --- | --- | --- |
| Start | hiring-start | Setup and a 6 line summary of your company | Answer the browser question, give name, website, a page, say yes |
| Plan | hiring-plan | Role, quantity, budget, timeline, hire or automate, funnel numbers | Confirm the defaults |
| Scorecard | hiring-scorecard | Weighted job related criteria, approved before scoring | Approve |
| Post and form | hiring-post | Posts per platform, the application form | Paste the posts, say yes to the form |
| Source | hiring-source | A clean prospects list and the strings for your own board searches | Run board searches, paste results |
| Screen | hiring-screen | Scores with evidence and a shortlist | Decide |
| Outreach | hiring-outreach | Drafts held for approval | Say yes, press send |
| Interview | hiring-interview | Kits, work sample, debrief, references, offer | Interview, decide |
| Weekly | hiring-pipeline | Where the funnel leaks and one change | Read, approve |

Ask anything about hiring at any time: the `hiring-advisor` skill answers from `docs/knowledge/`.

## Where files go

```
config/profile.json            your setup and company summary (git ignored)
hiring/company.md              the confirmed company summary
hiring/<role>/plan.md          the plan
hiring/<role>/scorecard.json   the approved scorecard
hiring/<role>/prospects.csv    prospects
hiring/<role>/inbox/           exports and pasted resumes
hiring/<role>/candidates/      candidates.jsonl
hiring/<role>/scores.json      scores
hiring/<role>/shortlist.csv    the shortlist
hiring/<role>/drafts/          posts, messages, form script
hiring/<role>/pipeline.csv     stage tracking
hiring/<role>/WEEKLY.md        weekly review
```

## Candidate record (one JSON per line in candidates.jsonl)

`candidate_id`, `role_id`, `source` (form, email, board_export, sourced, referral), `name`, `email`, `phone`, `location`, `links`, `resume_text`, `answers`.

## How a score is made

weighted score = sum of (weight x level / 4) over the scorecard criteria, level 0 to 4 per criterion. Tiers: strong (75 or more, every must at its minimum level, no failed gate), maybe (55 or more), below (under 55 or a must missing: not shortlisted now), review (any flag: instruction injection, low confidence, unknown gate). A candidate with a flag or low confidence needs a person.

## Engines

| Engine | What | When |
| --- | --- | --- |
| Claude (import) | Claude reads redacted candidates, writes levels and evidence | default, always works |
| Jev | fast typed scoring with confidence | optional, see JEV-OPTIONAL.md |
| rules | keyword baseline, offline, free | a sanity check only |
| mock | a fake Jev for practice | learning the tools |
