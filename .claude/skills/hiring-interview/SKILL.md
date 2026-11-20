---
name: hiring-interview
description: Builds structured interview kits, work samples, scheduling, debriefs, reference checks, the offer and the first 30 60 90 days. Use when the user says interview, questions to ask, work sample, schedule, references, offer, or onboarding.
---

# Hiring interview, reference, offer

Read `docs/knowledge/10-INTERVIEWS-AND-WORK-SAMPLES.md` and `11-REFERENCES-OFFERS-AND-ONBOARDING.md`.

## Interview kit

1. `python3 tools/interview_kit.py hiring/<role>/scorecard.json --out hiring/<role>/interviews/` writes the guide and a rating sheet. Every question maps to a scorecard criterion, with signs of a good and a weak answer.
2. Use the same questions in the same order for every candidate in a round. Add 1 or 2 follow up probes, never a question about family, age, health, religion or origin.
3. Work sample (`scorecard.work_sample`): short, realistic, paid when it is long. Give a time limit and the scoring guide before the candidate starts.

## Scheduling

Ask for the owner's availability, time zone and a booking link if they have one. Propose 3 slots, write the invite from `templates/messages/09-interview-invite.md`, and prepare the reminder. In browser mode, with a yes, create the calendar events in the owner's own calendar. Otherwise give the text and the details to paste. Never send invitations without a yes.

## After interviews

1. Collect each interviewer's ratings separately first (`templates/interviews/rating-sheet.md`), then debrief (`debrief.md`): discuss evidence per criterion, not gut feel.
2. Compare with the screen score. Say plainly where the interview changed the picture.
3. Reference checks: `templates/interviews/reference-check.md`, 5 questions that tell you something, only with the candidate's permission.
4. Offer: `offer-checklist.md` and `templates/messages/16-offer.md`: role, pay, start date, conditions, deadline. Say it is not legal advice and an employment lawyer or local template should review the contract. Plan for a decline: keep the next candidate warm.
5. Welcome and onboarding: `templates/messages/19-welcome-accepted.md` and `onboarding-30-60-90.md`.

## Rules

A person decides every hire and every no. Update `pipeline.csv` after each step (`hiring-pipeline`). Candidates hear back quickly. No question that is not job related.
