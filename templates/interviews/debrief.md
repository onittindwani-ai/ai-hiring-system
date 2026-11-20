# Debrief: {{role_title}}

A short meeting (30 minutes at most per finalist) where the interviewers compare scores and agree a recommendation for the owner. The owner decides. Run it only after every interviewer has submitted a rating sheet on their own.

Date: {{debrief_date}}   Owner or decider: {{decider_name}}   Interviewers: {{interviewer_names}}

## Ground rules

1. Everyone has scored alone first. No one changes a score because someone senior disagrees. Changes need new evidence.
2. Speak in evidence ("they said they cut returns by a third by changing the checklist"), not in feelings ("I just liked them").
3. Talk about the criteria, in order. No comments about age, gender, accent, looks, family or background. If it comes up, the facilitator stops it.
4. The person who scored lowest speaks first on each criterion, so the group hears the doubt before the praise.
5. A "no" or an offer is the owner's decision, and the reason is written down in job related words.

## Agenda

1. Scores side by side (5 minutes). Fill the table below.
2. Big gaps (10 minutes): any criterion where interviewers differ by 2 or more points. What did each person hear?
3. Gates, deal breakers and open questions (5 minutes). What do we still need (a reference, a second look at the work sample)?
4. Recommendation (5 minutes). Hire, hold, or not shortlisted, with one reason.
5. Next step and who tells the candidate, and when (5 minutes).

## Scores side by side

| Criterion | Interviewer 1 | Interviewer 2 | Interviewer 3 | Work sample | Gap 2 or more? | Agreed level |
| --- | --- | --- | --- | --- | --- | --- |
| {{criterion_1}} |  |  |  |  |  |  |
| {{criterion_2}} |  |  |  |  |  |  |
| {{criterion_3}} |  |  |  |  |  |  |
| {{criterion_4}} |  |  |  |  |  |  |

## Decision record

- Weighted score: {{weighted_score}}
- Must criteria all at or above the minimum? yes or no
- Gates and deal breakers: {{gates_status}}
- Missing information: {{missing_information}}
- Recommendation: hire, hold, or not shortlisted now
- Reason in one job related sentence:
- Decided by (name and date):

## After the meeting

- [ ] Update the pipeline: `python3 tools/pipeline.py move <candidate_id> <stage>`.
- [ ] Send the next message (reference request, offer or decline) after the decider approves it.
- [ ] Keep this record for the time your policy says, then delete it. Not legal advice.
- [ ] Add what you learned to the next version of the scorecard (a question that did not help, a criterion that was missing).

## Common traps in a debrief

- **Halo effect:** one great answer lifts every score. Check each criterion on its own.
- **Similar to me:** liking someone because they remind you of yourself. Ask: what job related evidence do I have?
- **Recency:** the last candidate feels best. Use the written scores of all candidates, side by side.
- **Gut feel:** "I just have a feeling" is not a reason. Ask the person to name the evidence behind it. If there is none, it does not count.
- **Pressure to fill the seat:** a hire you doubt is more costly than a gap. If the scores say hold, hold and keep sourcing.
- **Anchoring on the first score you hear:** that is why everyone scores alone first.
