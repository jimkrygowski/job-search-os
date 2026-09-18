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

**Tier 4 also needs, one time only:** LinkedIn allowed as a site in the
Claude in Chrome extension, and a logged-in LinkedIn session in that
browser. If either is missing, Tier 4 reports it and the scan continues.

1. Check the date and time.
2. Write the date and time to the console using the following pattern: Morning Scan for [DATE] [TIME]
3. Read `state/tracker.md` (the source of truth for pipeline state) so the scan is grounded in each company's current stage, last activity, and next action before pulling email/calendar.
4. Run Tiers 1-3 in parallel, **then** Tier 4 — it is browser-driven and
   slower, so running it last keeps it from delaying the others.
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
sources and run each in parallel with Tier 1.

**Do not pass `includeTrash: true` unless the source entry says to.** A
trashed digest is the user's own triage — they read it and judged it to
hold no new or relevant jobs. `search_threads` excludes Trash by default,
which is exactly the right filter. Never re-surface a listing from a
trashed digest.

Only if a source entry states that its digests are trashed automatically
rather than by hand, pass `includeTrash: true` for that source. `get_thread`
cannot read trashed messages (permission error) — rely on the
`search_threads` snippet, and if that is insufficient, say the message is
trashed and ask the user to restore it.

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

Recruiter and hiring-manager outreach often arrives on LinkedIn and never
touches email.

### Read-only — no exceptions

**Never send, reply, accept, decline, archive, connect, withdraw, or mark
anything.** Read and report only. This restates `CLAUDE.md` guardrail #3,
which is instruction-level here: the `settings.json` deny-list covers
Gmail tool names and cannot reach a browser tool. If the user asks
mid-scan for a reply, draft it and let them send it.

Reading a thread may mark it read. That side effect is acceptable;
nothing else is.

### Window: last 24 hours, read or unread

Match Tier 1's window. **Do not filter on unread** — read state tracks
"glanced at," not "handled."

Rows carry absolute date stamps ("Sep 17"); same-day rows show a clock
time. Walk top-down, stop at the first row older than 24h. At an
ambiguous boundary, include rather than drop.

### Procedure

1. `tabs_context_mcp`, then `tabs_create_mcp` — never reuse the user's tab.
2. `navigate` to `https://www.linkedin.com/messaging/`. This auto-opens
   the most recent thread; expected.
3. Read the list via `read_page` with `ref_id` set to the
   `list "Conversation List"` element, `depth: 4`. A full-page read
   truncates (~42K chars vs ~7K). Refs change every load — never reuse one.
4. Each row gives sender, date stamp, snippet. A `You:` snippet prefix
   means the user spoke last; a contact-name prefix means it awaits them.
   Carry that into the summary.
5. The list is virtualized — empty `listitem` entries are unrendered, not
   absent. If the 24h boundary isn't reached, click "Load more
   conversations."
6. Open each in-window thread (below) and capture sender, title, company,
   the ask, any role named, any comp/location stated.
7. `tabs_close_mcp`.

### Opening a thread

Get refs from `read_page` with `filter: "interactive"`, which collapses
each row to:

```
listitem [ref_N]
   generic [ref_N+1]    <- row body: the click target
   button  [ref_N+2]    <- options menu: never click
```

`left_click` with `ref` set to the row body `generic`.

- **Not the heading.** Headings, checkboxes and labels inside the row are
  inert — clicking one returns a successful `Clicked on element` and does
  nothing.
- **Not by coordinate.** `read_page` reports a 1920x1000 viewport while
  screenshots return varying smaller sizes (1536x800, 1210x630, 1382x675
  in one session); screenshot positions are scaled and stale.
- **No URL shortcut.** Rows carry no `href`.

After clicking, confirm the URL changed *and* the detail-pane header
shows the expected name before reading.

**Focused vs Other:** the "Focused" toggle switches views and InMail
lands in either — check both. Unverified as of 2026-09-18; report rather
than fight it if switching misbehaves.

### Cross-check against the pipeline

Classify every in-window thread against `state/tracker.md`:

- **Existing row** — report as activity on that opportunity.
- **Net-new** — report as net-new, and what it appears to be (recruiter
  outreach, warm intro reply, networking ask).
- **Noise** — recruiter blasts failing `state/career/trajectory.md`
  must-haves, sales pitches, newsletters. Give a skipped count in one
  line; do not enumerate.

### Report, do not act

**Do not create tracker rows, write `contacts.md`, or change any status
from this tier without the user saying so** — recruiter volume would fill
the tracker with dead entries. Once they say which matter, normal rules
apply, including `CLAUDE.md`'s standing instruction to record contacts.

### When it fails

Degrade, never block. LinkedIn won't load, session logged out, extension
lacks site permission, or structure drifted: say so in the summary, name
which if determinable, let the rest of the scan stand.

Stop after 2-3 failed calls and report what was tried — do not retry or
explore elsewhere on LinkedIn. Never trigger a JavaScript dialog; a modal
ends the session's browser access.

## Summary Format

**Pipeline** — one line per company with new activity. Flag replies, silence-breaks, or next actions due.

**LinkedIn** — one line per message worth attention, marked as either
activity on an existing opportunity or net-new. Note how many were
skipped as noise. If the tier could not run, say so in one line and why.

**Job alerts** — table of new listings worth flagging. Skip anything that doesn't fit. If nothing fits, say so in one line.

**Calendar** — bullet list of the week. Call out anything job-search-relevant.
