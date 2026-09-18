---
name: morning-scan
description: Use when the user asks for the morning email, LinkedIn and calendar check. Runs a structured daily scan of the job search pipeline, job alert feeds, LinkedIn messages, and calendar, and records new interview/deadline events found on the calendar to the tracker.
---

# Morning Scan

## Tools required
This skill uses the following tools. Add them to your always-allow list in Claude Code settings to avoid approval prompts on every run:

- `ToolSearch` — needed to load deferred tool schemas
- `mcp__claude_ai_Gmail__search_threads`
- `mcp__claude_ai_Gmail__get_thread`
- `mcp__claude_ai_Google_Calendar__list_events`
- `mcp__claude-in-chrome__*` — Tier 4 only (see that tier for the specific tools)

**Setup (first run only):** Load all tool schemas in one call before running the tiers:
```
ToolSearch: select:mcp__claude_ai_Gmail__search_threads,mcp__claude_ai_Gmail__get_thread,mcp__claude_ai_Google_Calendar__list_events,mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__find,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__tabs_close_mcp
```

**Tier 4 also needs, one time only:** LinkedIn granted as an allowed site
in the Claude in Chrome extension, and an active logged-in LinkedIn
session in that browser. Neither is something this skill can arrange; if
either is missing, Tier 4 reports that and the scan continues.

1. Check the date and time.
2. Write the date and time to the console using the following pattern: Morning Scan for [DATE] [TIME]
3. Read `state/tracker.md` (the source of truth for pipeline state) so the scan is grounded in each company's current stage, last activity, and next action before pulling email/calendar.
4. Run Tiers 1-3 in parallel. **Then** run Tier 4, which is browser-driven
   and materially slower than the other three combined — running it last
   means a slow or broken LinkedIn never delays the fast tiers.
5. Summarize — cross-check findings from all four tiers against
   `state/tracker.md` and flag any mismatches (e.g. a "next action" already
   resolved, a stage that's stale).

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
sources and run each in parallel with Tier 1. **Always pass
`includeTrash: true` on these `search_threads` calls.** Confirmed
2026-08-27: job alert digests can land in Trash (a filter or routine
cleanup may move them there), and `search_threads` excludes Trash by
default — the default query silently skips trashed digests entirely,
including same-day ones. `get_thread` cannot read trashed messages
(permission error); if a match is in Trash, rely on the `search_threads`
snippet for content, and if that's insufficient, tell the user the
message is trashed and ask them to restore it.

For each source, extract job listings (title, company, location, comp)
and flag any that match the must-haves in `state/career/trajectory.md`.
Skip the rest.

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

**Also check for resolved pending confirmations beyond the week window.**
The week-window fetch above is for routine visibility only — it cannot
surface a confirmation that lands further out. So separately: for every
`state/tracker.md` row whose Next Action reads as a pending
scheduling/confirmation ask (contains language like "confirm,"
"awaiting," "requested," or has a `TBD` Next Action Date), run a
targeted search — `list_events` with `fullText` set to the contact's
name or company — over the next 30 days. If it turns up a confirmed
event the tracker doesn't yet reflect, update the tracker
(`update-status`, with the real date/next-action) before writing the
summary, and report it as newly resolved rather than repeating the
stale line.

## Tier 4 — LinkedIn Messages

Recruiter and hiring-manager outreach frequently arrives on LinkedIn and
never touches email, so Tiers 1-2 cannot see it. Confirmed 2026-09-18:
three separate live conversations — two of them already scheduled calls
— originated as LinkedIn messages and were invisible to the
email-and-calendar scan until they surfaced indirectly as calendar
bookings days later. That is the gap this tier closes.

### Read-only — no exceptions

**This tier never sends, replies to, accepts, declines, archives,
connects, withdraws, or marks anything.** It reads and reports. This
restates guardrail #3 in `CLAUDE.md` at the tier level because that
guardrail is instruction-level only for browser automation: the
`.claude/settings.json` deny-list covers three Gmail tool names and
cannot reach a browser tool driving LinkedIn's web UI. Nothing the user
asks for mid-scan relaxes this — if they want a reply sent, draft it and
let them send it themselves.

Do not click anything that could send or change state. Reading a thread
may mark it read on LinkedIn's side; that is an unavoidable side effect
of reading and is acceptable. Nothing else is.

### Window: last 24 hours, read or unread

Match Tier 1's window. **Do not filter on unread** — the user reads
messages on their phone during the day, so read state tracks "glanced
at," not "handled," and filtering on it silently drops real items.

LinkedIn has no date-filter equivalent to Gmail's `newer_than:1d`. The
thread list is ordered most-recent-first and each row carries an
**absolute date stamp — "Sep 17", "Sep 16"** (confirmed 2026-09-18), not
a relative "2h"/"3d". Same-day threads show a clock time instead. So
walk the list top-down and stop at the first thread whose stamp predates
the 24h boundary. This is an approximation of the window, not a query —
if a stamp is ambiguous at the boundary, include the thread rather than
dropping it.

### Procedure

1. `tabs_context_mcp` first, to see the current browser state.
2. Open a **new** tab with `tabs_create_mcp` — do not reuse or navigate
   a tab the user is working in.
3. `navigate` to `https://www.linkedin.com/messaging/`. Note this
   auto-opens the most recent thread in the detail pane; that is normal.
4. **Read the conversation list with `ref_id` targeting, not a bare
   `read_page`.** Confirmed 2026-09-18: a full-page read returned 42,514
   characters and truncated, while the conversation list alone
   (`read_page` with `ref_id` set to the `list "Conversation List"`
   element, `depth: 4`) returned 7,353 — the same rows, a fifth of the
   budget. Do one cheap `read_page` with a small `depth` to locate that
   list's ref, then target it. Refs change every load; never reuse one
   from a previous run.
5. Each row gives sender, date stamp, and a snippet. **The snippet's
   prefix tells you who spoke last** — a `You: ...` prefix means the
   user sent the last message and the ball is in the other party's
   court; a contact-name prefix means it is waiting on the user. Carry
   that distinction into the summary; it is the difference between a
   silence-break and an open loop of the user's own.
6. Expect empty `listitem` entries in the list and a "Load more
   conversations" button at the bottom — the list is virtualized. Empty
   rows are unrendered, not missing data. If the 24h boundary has not
   been reached by the end of the rendered rows, load more rather than
   assuming the list ended.
7. For each thread inside the window, open it and read the message body.
   Capture: sender name, their title and company, what they are actually
   asking, any role named, and any comp/location detail stated.
8. Close the tab with `tabs_close_mcp` when done.

**Focused vs Other:** the inbox has a "Focused" toggle button that
switches views, and recruiter InMail can land in either. Check both.
Caveat: this toggle was the one step *not* exercised on the first live
run (2026-09-18) — the Focused view alone covered the window. If
switching misbehaves, report it rather than fighting it.

### Cross-check against the pipeline

For every thread inside the window, classify it against
`state/tracker.md` (already read in step 3):

- **Maps to an existing row** — report as activity on that opportunity,
  same as a Tier 1 email hit.
- **Net-new** — report it as net-new and say what it appears to be
  (recruiter outreach, a warm intro reply, a networking ask).
- **Noise** — generic recruiter blasts for roles that plainly fail
  `state/career/trajectory.md` must-haves, sales pitches, newsletters.
  Say how many were skipped in one line; do not enumerate them.

### Report, do not act

Surface findings and recommend. **Do not create tracker rows, write
`contacts.md` entries, or change any opportunity's status from this tier
without the user saying so.** LinkedIn recruiter volume is high enough
that auto-adding would fill the tracker with dead entries inside a week.
Once the user says which ones matter, the normal rules apply — including
`CLAUDE.md`'s standing instruction to record new contacts.

### When it fails

Degrade, never block. If LinkedIn will not load, the session is logged
out, the extension lacks site permission, or the page structure has
changed enough that the thread list cannot be read: **say so plainly in
the summary, name which of those it was if determinable, and let the
rest of the scan stand.** A failed Tier 4 is a reported gap, not a
failed scan.

Per the browser-automation guidance: if a tool call fails 2-3 times, or
the page stops responding, stop and tell the user what was tried. Do not
keep retrying, and do not go exploring elsewhere on LinkedIn. Never
trigger a JavaScript dialog — a modal blocks the extension entirely and
ends the session's browser access.

LinkedIn's DOM is unstable and changes without notice. This tier
deliberately describes *what to look for* rather than hardcoding
selectors. If the structure has drifted, report that rather than
guessing at replacements mid-scan.

## Summary Format

**Pipeline** — one line per company with new activity. Flag replies, silence-breaks, or next actions due.

**LinkedIn** — one line per message worth attention, marked as either
activity on an existing opportunity or net-new. Note how many were
skipped as noise. If the tier could not run, say so in one line and why.

**Job alerts** — table of new listings worth flagging. Skip anything that doesn't fit. If nothing fits, say so in one line.

**Calendar** — bullet list of the week. Call out anything job-search-relevant.
