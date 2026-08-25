---
name: interview-review
description: Use when a user has a call/interview transcript to review. Produces structured feedback, appends it to the opportunity's notes.md, and advances the tracker stage.
---

# Interview Review

## Purpose

Turn a call transcript into structured feedback and move the pipeline
state forward.

## Session Start

Identify which opportunity this call was for. If the transcript needs
cleaning up first (a raw recording, not yet summarized), run the
`summarize-call` command on it first.

## Review Contents

1. **What was covered** — brief factual summary.
2. **What went well / what to improve** — direct, specific feedback, not
   generic encouragement. Cite specific moments in the transcript.
3. **New information learned** — anything that changes the picture of
   this opportunity (comp signal, team structure, timeline, concerns
   raised by the interviewer). This is exactly the kind of signal that
   might mean `career/trajectory.md` needs a revisit — flag it explicitly
   if it contradicts a stated must-have or must-not, and suggest running
   `define-trajectory` in revisit mode if so.
4. **Recommended next stage / next action.**

## Output

1. Append the review under `## Interview Review (<date>)` in
   `opportunity/<Company>/<Role>/notes.md`. Include a line noting
   the source transcript, e.g. `Source: transcripts/<filename>`.
2. Save the transcript itself to
   `opportunity/<Company>/<Role>/transcripts/` if it isn't already there.
3. Advance the tracker:
   ```
   python3 tools/tracker.py update-status "<Company>" "<Role>" \
     --stage "<new stage>" --next-action "<next action>" \
     --next-action-date "<date, if known>"
   ```

## Guardrails

- Feedback must cite the transcript, not general impressions.
- Never call `tracker.py close` from this skill — closing is a pipeline
  decision the user makes explicitly, not an automatic consequence of a
  bad interview.
