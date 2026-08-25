---
name: score-opportunity
description: Use when a user pastes a job description to evaluate, or wants to re-score an opportunity already in the pipeline. Scores against state/career/trajectory.md, creates the opportunity folder, and adds it to the tracker via tools/tracker.py.
---

# Score Opportunity

## Purpose

Turn a job description into a scored, tracked opportunity.

## Session Start

Read `state/career/trajectory.md` (must-haves, must-nots, short-term goal) and
`state/career/profile.md`. If `state/career/trajectory.md` doesn't exist yet, tell the
user to run `bootstrap` or `define-trajectory` first — scoring without a
trajectory to score against isn't meaningful.

## New Opportunity (JD pasted in chat)

1. Identify Company and Role from the JD.
2. Check whether `state/opportunity/<Company>/<Role>/` already exists. If so,
   treat this as a re-score (below) instead.
3. Score the JD against `trajectory.md`'s must-haves and must-nots
   explicitly — go through each one and say whether the JD satisfies it,
   contradicts it, or doesn't say. Don't produce a single vague score
   without this breakdown.
4. Create `state/opportunity/<Company>/<Role>/jd.md` with the full JD text plus
   the scoring breakdown.
5. Add it to the tracker:
   ```
   python3 tools/tracker.py add "<Company>" "<Role>" --stage "Identified" \
     --next-action "<what the user should do next>" \
     --next-action-date "<date, if known>"
   ```
6. Tell the user the result plainly, including if it scores poorly — cite
   the specific must-have/must-not it fails, don't soften it.

## Re-scoring an Existing Opportunity

Read the existing `state/opportunity/<Company>/<Role>/jd.md` and
`state/opportunity/<Company>/<Role>/notes.md`, re-run the must-have/must-not
breakdown against the current `state/career/trajectory.md` (useful right after
a trajectory revisit), and append the updated scoring to `jd.md` with
today's date rather than overwriting the original scoring.

## Guardrails

- Every score must cite the specific trajectory criterion it's based on.
  No unsupported "this feels like a good fit."
- Never call `tracker.py update-status` or edit `state/tracker.md` directly
  from this skill — use `add` for new opportunities only. Stage changes
  after this point belong to other skills (`interview-review`,
  `morning-scan`) or a direct user request.
