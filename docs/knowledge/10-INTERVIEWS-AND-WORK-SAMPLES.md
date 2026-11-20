# 10. Interviews and work samples

## Purpose
Find out, with the least bias and the least wasted time, whether a person can do the job.
Same questions, same scoring, real work where possible, and fast feedback.

## The big idea in five lines
1. Ask every candidate for the same role the same core questions, in the same order.
2. Every question comes from a scorecard criterion. If it maps to no criterion, cut it.
3. Rate each answer on the scorecard levels, with a note, before anyone talks about it.
4. A small, real work sample beats a clever question. Pay for it when it is long.
5. Tell candidates what to expect and answer within a promised time.

## Do this
1. Start from `scorecard.json`. Run `tools/interview_kit.py hiring/<role>/scorecard.json` to produce `interview-guide.md` and `rating-sheet.csv`. Read both and edit.
2. Choose the stages. Keep them few:
   - Stage A: 20 to 30 minute screen call (gates, pay, interest, logistics, 2 or 3 core questions).
   - Stage B: structured interview (45 to 60 minutes) on the `must` criteria.
   - Stage C: work sample (see below), when the job produces something you can see.
   - Stage D: a short conversation with the person they will work with, and a chance for them to ask anything.
   Smaller businesses can merge B and D. Do not run five rounds for a part time role.
3. Assign interviewers by criterion. Each criterion is covered by at least one person. Two interviewers for B if you can.
4. Brief interviewers: the scorecard, the questions, the rating levels, and the "never ask" list.
5. Send the candidate a prep note: the stages, who they meet, how long, what to bring, how to ask for adjustments, and when they will hear back.
6. During the interview: ask the question as written, follow with "what did you do yourself?" and "what happened as a result?", take notes of what they say (not impressions).
7. Right after, each interviewer rates alone, in the sheet, before any chat. Level 0 to 4 per criterion plus one line of evidence.
8. Debrief (below). Decide with the evidence. Write the reason.
9. Tell the candidate the outcome inside the promised window.

## Designing questions from the scorecard
For each `must` criterion write two question types:
- Past behavior: "Tell me about a time you {{task}}. What was the situation, what did you do, what happened?"
- Realistic scenario: "Here is a situation in our business: {{scenario}}. What would you do first, and why?"
Each question carries:
| Part | Example (made up, bookkeeper at Northlight Home Services) |
| --- | --- |
| Criterion | Month end close |
| Question | Walk me through the last time you closed the books for a month. What did you check, and what went wrong? |
| Good signs | names a repeatable checklist, reconciles bank and card accounts, says what they would change |
| Weak signs | vague steps, "my boss did that", no checking |
| Follow ups | How long did it take? How did you know it was right? |
Rules for good questions:
- Open, specific, about work. Not trivia, not riddles, not "where do you see yourself in 5 years".
- No leading questions ("you are good with spreadsheets, right?").
- No hypothetical you cannot score. If you cannot say what a 4 looks like, rewrite it.
- Allow a moment to think. Silence is fine.
- 4 to 6 core questions for a 45 minute interview. More is not better.

## Questions never to ask
Age, birth year, graduation year used to guess age, marital or family status, children or plans for them, pregnancy, religion, origin, nationality or citizenship beyond "can you legally work here", health or disability, accent or "where are you really from", past pay in places where it is banned (verify locally, doc 12), arrests or convictions unless the law and the job allow it (verify locally). If a candidate volunteers something personal, do not record it as an input to the decision.
Ask instead: "Can you work the hours this job needs?", "Is there anything you need to do your best in this interview?"

## Work samples
A work sample is a small piece of the real job done by the candidate. It is often the best predictor you can get cheaply, and it is fairer than a trick question when the same brief is used for everyone.
1. Make it small and real: 30 to 90 minutes of work (starting assumption, replace with your own data) that looks like the first week on the job. Not free consulting on your real problem.
2. Same brief, same time limit, same scoring guide for everyone. Score blind (no names) with the criterion levels, using the scorecard's `work_sample.how_to_score`.
3. Pay for it when it takes more than about an hour, or when the work has real value. A fixed fee, the same for everyone, written in the invitation. Pay even if you do not hire.
4. Do not use their work. Do not ask them to fix a live problem of yours. Do not publish it.
5. Offer an alternative for people who cannot do a timed task (caring duties, a disability, a different time zone): a live walk through of past work, or a longer deadline.
6. Say which tools are allowed. If AI tools are allowed, say so. It may be what the job will use. If they are not, say why and how you will check.
7. Give feedback to finalists, even a short note.
Examples (made up) by role:
| Role | Work sample |
| --- | --- |
| Sales development rep | write a short first message to 3 fictional leads and a reply to an objection |
| Bookkeeper | reconcile a small fake bank file and list 3 questions you would ask the owner |
| Customer support | answer 4 sample tickets, one of them angry |
| Backend engineer | a small take home or a pair session on a real, simple problem, with a time cap |
| Video editor | edit a short sample clip you provide, and say what you would improve |

## Panel debriefs
1. Everyone's ratings are in the sheet before the meeting. No one speaks first about "who they liked".
2. The facilitator goes criterion by criterion. Show the ratings and quotes. Talk where ratings differ by 2 levels or more.
3. A gut feeling is allowed as a prompt to look for evidence, never as a reason. "I just did not like them" must become "what did they say or do?".
4. The hiring manager decides, after hearing all. The decision and the reason are written down.
5. Keep it short: 20 to 30 minutes per finalist.
6. Check the pool, not only the person: compare finalists with each other on the same criteria.

## Rating
- Use the 0 to 4 levels from the scorecard. Describe the evidence in one line.
- Rate each criterion on its own. Do not let one strong answer lift the rest (halo).
- Average only when criteria have equal weight. Otherwise use the weights, the same as in screening.
- Keep the notes. They are your record (doc 12).

## Bias traps
| Trap | What it looks like | Fix |
| --- | --- | --- |
| Similar to me | "I liked them, we have the same background" | score only against criteria; ask "which criterion did that touch?" |
| Halo | one great answer lifts everything | rate each criterion alone, before the debrief |
| Horns | one stumble sinks them | ask for the best evidence across all answers |
| First impression | the first 5 minutes decide | note-taking, structured order, late decision |
| Contrast | after a weak person, an ok one looks great | compare to the scorecard, not to the last candidate |
| Confidence over skill | a smooth talker beats a quiet expert | use work samples and "what did you do yourself?" |
| Accent or style | judging fluency instead of content | score the content; test language only if the job needs it |
| Culture fit | a vague "fit" | replace with a named, job related behavior |
| Anchoring on the resume | the number from screening drives the interview | interviewers rate fresh, from the interview only |

## Remote interviews
- Test the link and the tool with the candidate in the invitation. Offer a phone call as a backup.
- Send times in their time zone. Keep calls inside normal hours for both sides when possible.
- Do not judge the background, the lighting, a child or pet, or the camera quality. Do not require cameras on unless the job needs it.
- Allow short pauses for lag. Repeat questions in the chat if the line is poor.
- Record only with consent, and say how long you keep it (doc 12).
- Never use AI tools to judge voice, face, emotion or "energy" in a video interview. Those are unreliable and risky (doc 12). A transcript for note taking, with consent, is fine.
- Do not run an AI assistant that talks to the candidate in place of a person without telling them first and offering a human option.

## Speed of feedback
- Tell candidates the timeline at each stage. Then keep it.
- Starting assumption (replace with your own data): reply within 1 working day after an interview with "we got it, here is when you will hear", and a decision within 5 working days.
- Good people accept other offers. A slow process loses them.
- A weekly pipeline review (`tools/pipeline.py weekly`) shows who is stale.

## Common mistakes
- Different questions for each person, then comparing.
- Interviewing before the scorecard is clear.
- Too many rounds, too many people.
- A free big take home project that is really your own work.
- Talking about the debrief outcome before everyone wrote their ratings.
- Asking something personal "to make small talk".
- Using video AI to read emotions or personality.
- Letting the loudest person decide.
- Forgetting to tell the candidate the process and the dates.

## Numbers
- Core questions: 4 to 6 per 45 minute interview (starting assumption).
- Work sample: 30 to 90 minutes, paid when over about 1 hour (starting assumption).
- Debrief: 20 to 30 minutes per finalist (starting assumption).
- Interviews needed per hire: from your own funnel (`tools/funnel_calculator.py --actual hiring/<role>/pipeline.csv`). Before you have data, the funnel tool plans about 10 interviews for one hire (starting assumption, replace with your own data).

## Ask the owner
1. Who will interview, and who decides? Default: the hiring manager decides, one colleague co interviews.
2. Do you want a work sample, and can you pay for it? Default: yes if the job produces something visible, with a fixed fee if over 1 hour.
3. Are AI tools allowed in the work sample? Default: yes, if the job uses them, and say so in the brief.
4. How fast can you give feedback? Default: reply in 1 working day, decide in 5.
5. Do you need to run interviews in more than one language or time zone? Default: one language, times shown in the candidate's zone.
