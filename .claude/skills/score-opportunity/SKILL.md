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
2. Resolve the opportunity folder path — always through the tool, never by
   constructing `<Company>/<Role>` yourself, so folder naming stays
   consistent across sessions and skills (e.g. "VP Engineering" and
   "VP  Engineering" must land in the same folder, not two different
   ones):
   ```
   python3 tools/tracker.py opportunity-path "<Company>" "<Role>"
   ```
3. Check whether that folder already exists. If so, treat this as a
   re-score (below) instead.
4. Score the JD against `trajectory.md`, using `tools/score_table.py` so
   the criteria list and table format are always the same, never
   freehand:
   1. Run `python3 tools/score_table.py criteria` to get the exact
      criteria — every must-have, every must-not, and the short-term
      goal — parsed straight from `trajectory.md`, each with a stable
      `id`. Score against this list, not your own paraphrase of the
      document.
   2. For every criterion in that list, judge one of `Meets`, `Partial`,
      `Fails`, or `Unknown`, with a one-line rationale that cites the
      specific JD text it's based on. Don't skip any — the tool will
      reject an incomplete submission.
   3. Pipe `[{"id", "score", "rationale"}, ...]` as JSON into
      `python3 tools/score_table.py render` to get the formatted table.
      If it exits non-zero (missing criterion, unknown id, bad score
      value), fix the input and re-run — don't hand-format a table
      yourself.
5. Create `jd.md` inside the resolved folder, with the full JD text plus
   the rendered scoring table.
6. Add it to the tracker:
   ```
   python3 tools/tracker.py add "<Company>" "<Role>" --stage "Identified" \
     --next-action "<what the user should do next>" \
     --next-action-date "<date, if known>"
   ```
   (`add` stores the Company/Role you typed, unslugified, so the tracker
   table stays human-readable — only the folder name is slugified.)
7. Tell the user the result plainly, including if it scores poorly — cite
   the specific must-have/must-not it fails, don't soften it.

## Re-scoring an Existing Opportunity

Resolve the folder path the same way (`opportunity-path`), then read the
existing `jd.md` and `notes.md` inside it, re-run the scoring steps above
against the current `state/career/trajectory.md` (useful right after a
trajectory revisit), and append the updated table to `jd.md` under a
heading with today's date, rather than overwriting the original scoring.

## Guardrails

- Every score must cite the specific trajectory criterion it's based on
  (the table's Rationale column) — no unsupported "this feels like a
  good fit."
- Always use `tools/score_table.py` to build the table — never hand-write
  a Markdown table for this. That's what keeps the format identical
  across every scoring session.
- Never call `tracker.py update-status` or edit `state/tracker.md` directly
  from this skill — use `add` for new opportunities only. Stage changes
  after this point belong to other skills (`interview-review`,
  `morning-scan`) or a direct user request.
