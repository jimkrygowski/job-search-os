---
name: morning-scan
description: Use when the user asks for the morning email and calendar check. Runs a structured daily scan of the job search pipeline, job alert feeds, and calendar, and records new interview/deadline events found on the calendar to the tracker.
---

# Morning Scan

## Tools required
This skill uses the following tools. Add them to your always-allow list in Claude Code settings to avoid approval prompts on every run:

- `ToolSearch` — needed to load deferred tool schemas
- `mcp__claude_ai_Gmail__search_threads`
- `mcp__claude_ai_Gmail__get_thread`
- `mcp__claude_ai_Google_Calendar__list_events`

**Setup (first run only):** Load all tool schemas in one call before running the tiers:
```
ToolSearch: select:mcp__claude_ai_Gmail__search_threads,mcp__claude_ai_Gmail__get_thread,mcp__claude_ai_Google_Calendar__list_events
```

1. Check the date and time.
2. Write the date and time to the console using the following pattern: Morning Scan for [DATE] [TIME]
3. Read `state/tracker.md` (the source of truth for pipeline state) so the scan is grounded in each company's current stage, last activity, and next action before pulling email/calendar.
4. Run all three tiers in parallel, then summarize — cross-check findings against `state/tracker.md` and flag any mismatches (e.g. a "next action" already resolved, a stage that's stale).

## Tier 1 — Pipeline Emails
Build the contact list dynamically rather than using a fixed list: read
`state/tracker.md` for active opportunities, then for each one resolve
its folder via
`python3 tools/tracker.py opportunity-path "<Company>" "<Role>"` (never
construct the path yourself from the Company/Role text in the tracker
row) and read that folder's `contacts.md` for known contact emails.
Search for new messages from all of them in the last 24 hours:

```
from:(<contact1> OR <contact2> OR ...) newer_than:1d
```

**Do not trust `search_threads`'s embedded message list as complete.** Confirmed 2026-08-05: for a 12-message thread, `search_threads` showed only the first 5 (oldest) messages and silently dropped the 3 most recent — including same-day replies. Relying on it directly caused a real new message from an active contact to be reported as "no new activity." For every thread `search_threads` matches, follow the three-tier method:

1. `search_threads` — use only to find which threads have *any* recent activity, not to read their content.
2. `get_thread` with `messageFormat: MINIMAL` on each matched thread — cheap call, returns true message count and dates. Compare the latest date here against what you already know from `state/tracker.md`/prior scans.
3. Only if that reveals genuinely new messages, call `get_thread` with `messageFormat: FULL_CONTENT`. If the result exceeds the token limit and gets saved to a file, run it through `tools/gmail_extract.py` (from this repo's root) instead of hand-parsing HTML/quoted history:
   ```
   python3 tools/gmail_extract.py <saved_thread.json> --latest 3
   ```
   (`--after YYYY-MM-DD` also works if you know the last-checked date.)

## Tier 2 — Job Alert Feeds

If `state/career/job_alert_sources.md` doesn't exist yet, copy
`.claude/skills/morning-scan/job_alert_sources.template.md` to that path,
then tell the user it needs real sources filled in before this tier can
do anything useful, and skip Tier 2 for this run.

Otherwise, read `state/career/job_alert_sources.md` for the configured
sources and run each in parallel with Tier 1. For each source, extract
job listings (title, company, location, comp) and flag any that match
the must-haves in `state/career/trajectory.md`. Skip the rest.

## Tier 3 — Calendar
List events from today through end of the week. For any event that's a
job search call/interview or a closing deadline for an opportunity in
`state/tracker.md`, persist it instead of only reporting it in chat:
```
python3 tools/tracker.py record-event "<Company>" "<Role>" \
  --event "<what the event is>" --date "<date>"
```
Flag any conflicts with expected pipeline activity in the summary as
well.

## Summary Format

**Pipeline** — one line per company with new activity. Flag replies, silence-breaks, or next actions due.

**Job alerts** — table of new listings worth flagging. Skip anything that doesn't fit. If nothing fits, say so in one line.

**Calendar** — bullet list of the week. Call out anything job-search-relevant.
