# Job Search Agent — Design

Status: approved by Jim, pending final spec review before implementation planning.
Supersedes the informal system at `~/code/job-search`, which stays live and
untouched until this system is built and data is migrated over (see
Migration, below).

## 1. Purpose

Assist a job seeker through the full arc of a search: clarifying what career
they're pursuing and why, building a resume and supporting stories that
reflect that career, identifying and scoring opportunities, and managing
each opportunity through the application/interview/negotiation pipeline.

Built for Jim's active search, but the engine is designed to be usable by
anyone — no personal facts are hardcoded into skills or commands. Success
is measured by reduced labor operating the search, not by feature count.

## 2. Non-Goals

- **No automation.** Nothing runs on a schedule or trigger. Every skill is
  invoked by the user, in chat, on demand — including the "daily" email and
  calendar review (`morning-scan`), which the user runs when they want it,
  not on a cron.
- **No autonomous sending.** The agent drafts correspondence; it never
  sends it. Enforced structurally, not just by instruction (see §7).
- **Not a replacement for human support.** Never Search Alone's Job Search
  Council (peer accountability group) is a real, human structure this
  system doesn't attempt to substitute for or manage.

## 3. Architecture

One repository, two zones:

- **Engine** — generic, contains no personal facts: `.claude/skills/`,
  `.claude/commands/`, `tools/*.py`, root `CLAUDE.md`. Skills read personal
  facts from data files at runtime rather than embedding them, which is
  what makes the engine reusable by someone else in principle.
- **Data** — personal, specific to whoever is running the search:
  `career/`, `opportunity/<Company>/<Role>/`, `tracker.md`,
  `tracker_closed.md`.

`CLAUDE.md` defines the persona once — direct, a peer and thought partner
rather than a cheerleader, states only facts it can source, never sends
correspondence — so individual skills inherit tone rather than each
redefining it (the current `career-coach` restates persona itself; the new
version won't need to).

## 4. Repository Layout

```
CLAUDE.md                        persona, guardrails, pointers to data files

career/
  profile.md                     candidate profile: bio, career history,
                                  reflections (built via `build-profile`)
  trajectory.md                  Mnookin Two-Pager–shaped target-role
                                  definition (built/revisited via
                                  `define-trajectory`) — see §6
  resume/
    master_resume.md             comprehensive source-of-truth resume

opportunity/<Company>/<Role>/
  jd.md
  contacts.md                    contacts + their roles
  notes.md                       meeting outcomes, research, new info —
                                  entries carry source + date
  resume.md                      tailored resume for this opportunity
  cover_letter.md
  transcripts/

tracker.md                       active opportunities — single markdown
                                  table, tool-managed only
tracker_closed.md                archived opportunities — kept out of
                                  default reads/context

tools/
  tracker.py                     add, update-status, list, close,
                                  record-event
  gmail_extract.py               carried over as-is

.claude/
  skills/
    bootstrap/                   new — onboarding orchestrator
    build-profile/                new
    define-trajectory/            new
    tailor-resume/                new
    score-opportunity/            new
    company-research/             new
    interview-prep/               new
    interview-review/             new
    career-coach/                 preserved, updated (see §6)
    morning-scan/                 preserved, updated (see §6)
  commands/
    summarize-call.md             preserved as-is (mechanical, no judgment
                                   call needed — fits a command, not a skill)
```

## 5. Data Model

**`career/trajectory.md`** follows the Mnookin Two-Pager shape (Never
Search Alone): what you love/hate doing, must-haves/must-nots, short- and
long-term goals, strengths/weaknesses. It's written to double as a real
shareable pitch document, not just internal notes. Carries a
`Last reviewed: <date>` field used by the revisit trigger (§8).

**`tracker.md`** / **`tracker_closed.md`** — one markdown table each,
minimal pipe padding (no column-alignment padding, to keep git diffs
quiet). Columns: Company, Role, Stage, Last Activity, Next Action, Next
Action Date. `tracker.py` is the only writer of either file — full-file
rewrite on every call, never a partial patch. `close` moves a row from
`tracker.md` to `tracker_closed.md` and appends the closing reason to that
opportunity's `notes.md`.

**`opportunity/<Company>/<Role>/notes.md`** — freeform, but entries carry a
source and date, since guardrail #2 (no unsupported opinions) is enforced
by convention here, not by tooling: an unsourced claim is visibly
unsourced rather than blended in.

## 6. Skills & Commands

New:

- **`bootstrap`** — first-time-setup orchestrator. Checks whether
  `career/profile.md` / `trajectory.md` already exist and resumes from
  wherever the user left off rather than forcing a restart. Runs
  `build-profile` then `define-trajectory` in sequence.
- **`build-profile`** — guided conversation to create/update
  `career/profile.md`, seeded from an existing resume if one exists.
  Covers career-to-date reflection: best/worst job, best/worst boss, and
  why.
- **`define-trajectory`** — two modes on the same skill: **initial**
  (build the Mnookin Two-Pager from scratch — target role, must/nice-to-
  haves, honest stretch/gap coaching) and **revisit** (detects an existing
  `trajectory.md` and updates it conversationally in place). See §8 for
  what triggers revisit mode.
- **`tailor-resume`** — per-opportunity resume + cover letter, built from
  `master_resume.md` and the opportunity's `jd.md`. Never invents
  experience (guardrail #1).
- **`score-opportunity`** — takes a pasted JD (or an existing opportunity),
  scores it against `trajectory.md`, creates/updates the
  `opportunity/<Company>/<Role>/` folder, calls `tracker.py add`. Also
  supports re-scoring an existing opportunity.
- **`company-research`** — researches a target company, writes cited
  findings to `notes.md`.
- **`interview-prep`** — briefing before a call, built from `jd.md`,
  `notes.md`, `contacts.md`, `trajectory.md`.
- **`interview-review`** — reads a call transcript, appends structured
  feedback to `notes.md`, calls `tracker.py update-status`.

Preserved, updated:

- **`career-coach`** — same coaching frameworks (Schein's Anchors, SDT,
  Ibarra, etc.), but reads facts from `profile.md`/`trajectory.md` instead
  of a hardcoded bio, and reads/writes `tracker.md` instead of
  `applications.csv`. Session-start protocol also checks `trajectory.md`'s
  `Last reviewed` date and flags staleness (§8).
- **`morning-scan`** — same three-tier email/job-alert/calendar logic, but
  now calls `tracker.py record-event` when the calendar tier finds a new
  interview or deadline, instead of only reporting it in chat. This is the
  concrete fix for the tracker-corruption problem: calendar-derived
  updates become tool-mediated instead of chat-edited.

## 7. `tracker.py`

CLI, no server, no dependencies beyond the standard library. Subcommands:

- `add <company> <role> --stage ... --next-action ... --next-action-date ...`
- `update-status <company> <role> --stage ... [--next-action ...] [--next-action-date ...]`
- `list [--closed]` — defaults to active only
- `close <company> <role> --reason "..."` — moves the row to
  `tracker_closed.md`, appends the reason to that opportunity's `notes.md`
- `record-event <company> <role> --event ... --date ...` — used by
  `morning-scan` to persist calendar-derived updates

Every write is a full-file rewrite of the target table, parsed and
re-serialized, never a line-level patch — this plus "the CLI is the only
writer" is the structural fix for the corruption the current
`applications.csv` workflow suffers from.

## 8. Trajectory Revisit Triggers

`trajectory.md` will drift out of date as the search progresses — what's
realistic and what's wanted both evolve. Two triggers, both surfaced
during an already-user-initiated session (consistent with the no-
automation non-goal — nothing runs in the background):

- **Time-based** — `career-coach`'s session start checks `trajectory.md`'s
  `Last reviewed` date; if it's more than 6 weeks old, it flags this and
  offers to run `define-trajectory` in revisit mode.
- **Signal-based** — informed by Never Search Alone's Listening Tour: real
  feedback (an interview outcome, a networking conversation, an explicit
  "if you were in my shoes" conversation) that contradicts current
  must-haves should trigger an immediate revisit, not wait for staleness.
  `interview-review` and `career-coach` both watch for this and prompt a
  revisit when they see it.

## 9. Guardrails & Enforcement

| Guardrail | Enforcement |
|---|---|
| Never invent experience on a resume | Instruction-level, in `tailor-resume` and `CLAUDE.md`. No technical gate exists for this. |
| Never assert unsupported opinions | Instruction-level, plus the source+date convention in `notes.md` (§5) so unsourced claims are visibly unsourced. |
| Never send correspondence autonomously | **Structural.** `.claude/settings.json` denies the Gmail send/reply/forward tools outright — only drafting tools stay allowed. The agent cannot send even if instructed to. |

## 10. Memory & State

Two distinct kinds of persistence, not to be conflated:

- **Pipeline/opportunity state** lives in the data files described above
  (`tracker.md`, `opportunity/.../notes.md`, etc.) — this is search
  content, versioned in the repo.
- **User preferences** (how Jim likes to work, standing corrections,
  collaboration style) use Claude Code's existing project memory system —
  this is infrastructure that already exists and needs no new building,
  just normal use.

## 11. Migration

Out of scope for this spec's implementation plan. Once the new system is
built and validated against a couple of real opportunities, migrate live
pipeline data from `~/code/job-search` (`companies/`, `applications.csv`,
`career/`) into the new layout by hand, opportunity by opportunity, rather
than a scripted bulk migration — the folder shape changed enough
(`companies/<Company>` flat → `opportunity/<Company>/<Role>/`, CSV → two
markdown tables) that a script would be more work than it saves for a
pipeline of this size.

## 12. Testing & Validation

- **`tracker.py`** gets real unit tests: add/update/list/close/record-event
  round-trip correctly; parsing survives special characters (commas,
  pipes, unicode in company/role names); an empty tracker file and a
  tracker with one row both work; `close` correctly moves rows and never
  duplicates or drops one.
- **Skills** are validated by manual dry-run walkthroughs (no test
  framework exists for prompt-driven behavior): run `bootstrap` on a clean
  checkout, run `score-opportunity` against a real pasted JD, confirm
  `morning-scan` calls `tracker.py record-event` rather than describing the
  update only in chat, confirm the Gmail send/reply/forward tools are
  actually denied by `.claude/settings.json`.

## 13. Open Questions

None currently — see `bootstrap-planning.md` for the raw inputs this spec
was built from.
