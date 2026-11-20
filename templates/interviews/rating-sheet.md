# Rating sheet: {{role_title}}

One sheet per interviewer per candidate. Fill it in on your own before the debrief. Score the evidence, not your feeling about the person. `python3 tools/interview_kit.py hiring/<role>/scorecard.json` also writes a CSV version.

Candidate: {{candidate_id}}   Interviewer: {{interviewer_name}}   Date: {{interview_date}}

## Scale (0 to 4, same as the scorecard)

- 0 no evidence
- 1 mentioned only
- 2 did it with help or at small scale
- 3 did it on their own with a clear result
- 4 did it, improved the method or taught others

Each `must` criterion has a minimum level in the scorecard. A score below the minimum means "not shortlisted now", and it is a person who decides.

## Scores

| Criterion | Type | Weight | Min level | My score (0 to 4) | Evidence (a short quote or fact) | Confidence (low, medium, high) |
| --- | --- | --- | --- | --- | --- | --- |
| {{criterion_1}} | must | {{weight_1}} | {{min_1}} |  |  |  |
| {{criterion_2}} | must | {{weight_2}} | {{min_2}} |  |  |  |
| {{criterion_3}} | must | {{weight_3}} | {{min_3}} |  |  |  |
| {{criterion_4}} | nice |  |  |  |  |  |
| {{criterion_5}} | nice |  |  |  |  |  |
| {{criterion_6}} | nice |  |  |  |  |  |

Weighted score = sum of (weight x score / 4). The tool does this for you. Do not change weights after you have met the candidate.

## Gates and deal breakers

| Item | Yes, no or unknown | Note |
| --- | --- | --- |
| {{gate_1}} |  |  |
| {{deal_breaker_1}} |  |  |

A deal breaker needs a clear fact from the candidate, not a hunch.

## Red flags seen (only job related)

- 

## Strengths seen

- 

## Open questions to check (reference, work sample or a second call)

- 

## My recommendation (a person decides, this is only input)

Choose one: strong yes, yes, unsure, no. Reason in one sentence tied to the criteria:

## Bias check before you submit (tick each)

- [ ] I scored only what the candidate said or did for the job.
- [ ] I did not use age, gender, accent, name, appearance, background, family situation or any guess about them.
- [ ] I did not compare them to someone I like or to myself.
- [ ] I did not let one strong or weak answer decide all scores (halo effect).
- [ ] Every score has evidence written down.
