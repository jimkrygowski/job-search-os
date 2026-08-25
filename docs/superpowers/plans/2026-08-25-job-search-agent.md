# Job Search Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the job search agent scaffold described in the design spec — a self-contained Claude Code project with a generic engine (skills, commands, tools) and a separate personal data layer, replacing the informal system at `~/code/job-search`.

**Architecture:** One repo, two zones. Engine (`.claude/skills/`, `.claude/commands/`, `tools/*.py`, root `CLAUDE.md`) contains no personal facts and reads them from data files at runtime. Data (`career/`, `opportunity/<Company>/<Role>/`, `tracker.md`, `tracker_closed.md`) is personal and gitignored-free (committed normally — this is the user's own repo).

**Tech Stack:** Python 3 standard library only (no pip dependencies, including for tests — uses `unittest`, not `pytest`). Claude Code skills/commands as markdown. No server, no database.

**Spec:** `docs/superpowers/specs/2026-08-25-job-search-agent-design.md`

## Global Constraints

- Engine is stdlib-only: no pip dependencies for anything under `tools/`, at runtime or in tests.
- `tools/tracker.py` is the only writer of `tracker.md` / `tracker_closed.md` — full-file rewrite every call, never a partial patch.
- Markdown tables use minimal single-space padding only — no column-alignment padding (keeps git diffs quiet).
- No automation. Every skill/command is invoked by the user in chat; nothing runs on a schedule or trigger.
- The agent never sends correspondence. Enforced via `.claude/settings.json` tool deny-list, not instruction alone.
- Skills and commands contain no hardcoded personal facts — they read `career/profile.md`, `career/trajectory.md`, and `opportunity/*/contacts.md` at runtime instead.
- `opportunity/<Company>/<Role>/notes.md` entries carry a source and a date.
- `career/trajectory.md` staleness threshold is 6 weeks (`Last reviewed:` field).

---

## Task 1: Repo Scaffolding

**Files:**
- Create: `CLAUDE.md`
- Create: `.claude/settings.json`
- Create: `.gitignore`

**Interfaces:**
- Produces: the persona/guardrail instructions every skill inherits; the tool deny-list that structurally blocks sending correspondence.

- [ ] **Step 1: Write `CLAUDE.md`**

```markdown
# Job Search Agent

You are a career coach and job search operator working with whoever is
running this repo. At the start of any substantive session, read
`career/profile.md` and `career/trajectory.md` if they exist — they are
the source of truth for who this person is and what they're looking for.
Do not assume facts about them beyond what's written there, in
`tracker.md`, or in `opportunity/*/notes.md`.

If `career/profile.md` doesn't exist yet, this is a new user — point them
at the `bootstrap` skill rather than improvising a setup flow.

## Persona

- Be direct. You are a peer and thought partner, not a cheerleader.
- State only facts you can point to a source for. If you're inferring or
  guessing, say so explicitly.
- Don't optimize for the user feeling good about their pipeline.
  Optimize for them being clear-eyed about it.

## Guardrails

1. **Never invent experience.** When tailoring a resume or cover letter,
   every claim must trace to `career/profile.md`,
   `career/resume/master_resume.md`, or something the user tells you
   directly in conversation. If there's a gap, say so — don't paper over
   it.
2. **Never assert unsupported opinions.** Findings written to
   `opportunity/*/notes.md` must carry a source and a date. If you don't
   have one, label the claim as your own inference, not a fact.
3. **Never send correspondence.** You may draft emails, but sending is
   denied at the tool level (see `.claude/settings.json`) as well as by
   this instruction. Don't attempt to work around the deny-list.

## Data Files

- `career/profile.md` — candidate profile (built by `build-profile`)
- `career/trajectory.md` — target role, Mnookin Two-Pager shape (built/
  revisited by `define-trajectory`)
- `career/resume/master_resume.md` — comprehensive source-of-truth resume
- `tracker.md` / `tracker_closed.md` — pipeline state. Managed only via
  `tools/tracker.py` — never hand-edit these files.
- `opportunity/<Company>/<Role>/` — per-opportunity documents (JD,
  contacts, notes, tailored resume/cover letter, transcripts)
```

- [ ] **Step 2: Write `.claude/settings.json`**

```json
{
  "permissions": {
    "deny": [
      "mcp__claude_ai_Gmail__send_message",
      "mcp__claude_ai_Gmail__reply",
      "mcp__claude_ai_Gmail__forward"
    ]
  }
}
```

- [ ] **Step 3: Write `.gitignore`**

```
__pycache__/
*.pyc
.DS_Store
.claude/settings.local.json
```

- [ ] **Step 4: Verify the settings file is valid JSON**

Run: `python3 -c "import json; json.load(open('.claude/settings.json'))"`
Expected: no output, exit code 0

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md .claude/settings.json .gitignore
git commit -m "Scaffold repo: persona, guardrails, and send-tool deny-list"
```

---

## Task 2: `tracker.py` — CLI and Library

**Files:**
- Create: `tools/tracker.py`
- Test: `tools/test_tracker.py`

**Interfaces:**
- Produces: `tracker.COLUMNS`, `tracker.ACTIVE_PATH`, `tracker.CLOSED_PATH`, `tracker.ACTIVE_TITLE`, `tracker.CLOSED_TITLE`, `tracker.read_table(path: Path) -> list[dict[str,str]]`, `tracker.write_table(path: Path, rows: list[dict[str,str]], title: str) -> None`, `tracker.serialize_table(rows, title) -> str`, `tracker.parse_table(text: str) -> list[dict[str,str]]`, `tracker.find_row(rows, company, role) -> dict|None`. CLI: `python3 tools/tracker.py {add,update-status,record-event,close,list} ...`. All later tasks (`score-opportunity`, `interview-review`, `morning-scan`) call the CLI form, never import the module directly.

- [ ] **Step 1: Write the test file**

```python
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import tracker  # noqa: E402


class TrackerLibTest(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self._tmpdir = tempfile.TemporaryDirectory()
        os.chdir(self._tmpdir.name)

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmpdir.cleanup()

    def test_read_table_missing_file_returns_no_rows(self):
        self.assertEqual(tracker.read_table(Path("tracker.md")), [])

    def test_write_then_read_round_trip(self):
        rows = [{
            "Company": "Altana", "Role": "VP Engineering", "Stage": "Screen",
            "Last Activity": "2026-08-19", "Next Action": "Follow up",
            "Next Action Date": "2026-08-26",
        }]
        tracker.write_table(Path("tracker.md"), rows, tracker.ACTIVE_TITLE)
        self.assertEqual(tracker.read_table(Path("tracker.md")), rows)

    def test_round_trip_survives_pipe_and_comma_in_cell(self):
        rows = [{
            "Company": "Bed | Bath & Beyond, Inc.", "Role": "CTO",
            "Stage": "Identified", "Last Activity": "2026-08-20",
            "Next Action": "", "Next Action Date": "",
        }]
        tracker.write_table(Path("tracker.md"), rows, tracker.ACTIVE_TITLE)
        self.assertEqual(tracker.read_table(Path("tracker.md")), rows)

    def test_no_column_alignment_padding(self):
        rows = [
            {"Company": "A", "Role": "Short", "Stage": "S",
             "Last Activity": "2026-01-01", "Next Action": "",
             "Next Action Date": ""},
            {"Company": "A Very Long Company Name Inc",
             "Role": "Longer Role Title", "Stage": "S",
             "Last Activity": "2026-01-01", "Next Action": "",
             "Next Action Date": ""},
        ]
        text = tracker.serialize_table(rows, tracker.ACTIVE_TITLE)
        short_row_line = [l for l in text.splitlines() if l.startswith("| A |")]
        self.assertEqual(short_row_line, ["| A | Short | S | 2026-01-01 |  |  |"])


class TrackerCLITest(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self._tmpdir = tempfile.TemporaryDirectory()
        os.chdir(self._tmpdir.name)
        self.tracker_py = str(Path(self._cwd) / "tools" / "tracker.py")

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmpdir.cleanup()

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, self.tracker_py, *args],
            capture_output=True, text=True,
        )

    def test_add_then_list_shows_new_row(self):
        result = self.run_cli(
            "add", "Altana", "VP Engineering",
            "--stage", "Identified", "--next-action-date", "2026-08-26",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli("list")
        self.assertIn("Altana", result.stdout)
        self.assertIn("VP Engineering", result.stdout)

    def test_add_duplicate_fails(self):
        self.run_cli("add", "Altana", "VP Engineering", "--stage", "Identified")
        result = self.run_cli("add", "Altana", "VP Engineering", "--stage", "Identified")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("already exists", result.stderr)

    def test_update_status_on_missing_row_fails(self):
        result = self.run_cli("update-status", "Nope", "Nowhere", "--stage", "X")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not found", result.stderr)

    def test_update_status_changes_stage_and_next_action(self):
        self.run_cli("add", "Altana", "VP Engineering", "--stage", "Identified")
        self.run_cli(
            "update-status", "Altana", "VP Engineering",
            "--stage", "Screen", "--next-action", "Call",
            "--next-action-date", "2026-09-01",
        )
        result = self.run_cli("list")
        self.assertIn("Screen", result.stdout)
        self.assertIn("Call", result.stdout)

    def test_record_event_updates_next_action_without_changing_stage(self):
        self.run_cli("add", "Altana", "VP Engineering", "--stage", "Screen")
        self.run_cli(
            "record-event", "Altana", "VP Engineering",
            "--event", "Onsite interview", "--date", "2026-09-05",
        )
        result = self.run_cli("list")
        self.assertIn("Screen", result.stdout)
        self.assertIn("Onsite interview", result.stdout)

    def test_close_moves_row_to_closed_and_writes_notes(self):
        self.run_cli("add", "Altana", "VP Engineering", "--stage", "Screen")
        result = self.run_cli(
            "close", "Altana", "VP Engineering",
            "--reason", "Role was put on hold",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        active = self.run_cli("list")
        self.assertNotIn("Altana", active.stdout)

        closed = self.run_cli("list", "--closed")
        self.assertIn("Altana", closed.stdout)

        notes = Path("opportunity/Altana/VP Engineering/notes.md").read_text()
        self.assertIn("Role was put on hold", notes)

    def test_close_missing_row_fails(self):
        result = self.run_cli("close", "Nope", "Nowhere", "--reason", "n/a")
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest tools/test_tracker.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'tracker'` (the file doesn't exist yet)

- [ ] **Step 3: Write `tools/tracker.py`**

```python
#!/usr/bin/env python3
"""CLI for reading and writing tracker.md / tracker_closed.md.

This is the only code that should ever write these files. Skills call it
via `python3 tools/tracker.py <command> ...` rather than editing the
markdown tables directly, to avoid corrupting pipeline state.
"""
import argparse
import datetime
import sys
from pathlib import Path

COLUMNS = ["Company", "Role", "Stage", "Last Activity", "Next Action", "Next Action Date"]

ACTIVE_PATH = Path("tracker.md")
CLOSED_PATH = Path("tracker_closed.md")
ACTIVE_TITLE = "Active Opportunities"
CLOSED_TITLE = "Closed Opportunities"


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def unescape_cell(value: str) -> str:
    return value.replace("\\|", "|").strip()


def split_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    parts = []
    current = ""
    i = 0
    while i < len(stripped):
        ch = stripped[i]
        if ch == "\\" and i + 1 < len(stripped) and stripped[i + 1] == "|":
            current += "\\|"
            i += 2
            continue
        if ch == "|":
            parts.append(current.strip())
            current = ""
            i += 1
            continue
        current += ch
        i += 1
    parts.append(current.strip())
    return parts


def parse_table(text: str) -> list[dict]:
    lines = [line for line in text.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return []
    rows = []
    for line in lines[2:]:  # skip header + separator
        cells = split_row(line)
        if len(cells) != len(COLUMNS):
            raise ValueError(
                f"Malformed row (expected {len(COLUMNS)} columns, got {len(cells)}): {line!r}"
            )
        rows.append({col: unescape_cell(cell) for col, cell in zip(COLUMNS, cells)})
    return rows


def serialize_table(rows: list[dict], title: str) -> str:
    header = "| " + " | ".join(COLUMNS) + " |"
    separator = "| " + " | ".join(["---"] * len(COLUMNS)) + " |"
    lines = [f"# {title}", "", header, separator]
    for row in rows:
        cells = [escape_cell(row.get(col, "")) for col in COLUMNS]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def read_table(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return parse_table(path.read_text())


def write_table(path: Path, rows: list[dict], title: str) -> None:
    path.write_text(serialize_table(rows, title))


def find_row(rows, company, role):
    for row in rows:
        if row["Company"] == company and row["Role"] == role:
            return row
    return None


def today() -> str:
    return datetime.date.today().isoformat()


def cmd_add(args):
    rows = read_table(ACTIVE_PATH)
    if find_row(rows, args.company, args.role):
        print(
            f"error: {args.company} / {args.role} already exists in tracker.md "
            "— use update-status",
            file=sys.stderr,
        )
        sys.exit(1)
    rows.append({
        "Company": args.company,
        "Role": args.role,
        "Stage": args.stage,
        "Last Activity": args.last_activity or today(),
        "Next Action": args.next_action or "",
        "Next Action Date": args.next_action_date or "",
    })
    write_table(ACTIVE_PATH, rows, ACTIVE_TITLE)
    print(f"added {args.company} / {args.role}")


def cmd_update_status(args):
    rows = read_table(ACTIVE_PATH)
    row = find_row(rows, args.company, args.role)
    if row is None:
        print(f"error: {args.company} / {args.role} not found in tracker.md", file=sys.stderr)
        sys.exit(1)
    row["Stage"] = args.stage
    if args.next_action is not None:
        row["Next Action"] = args.next_action
    if args.next_action_date is not None:
        row["Next Action Date"] = args.next_action_date
    row["Last Activity"] = args.last_activity or today()
    write_table(ACTIVE_PATH, rows, ACTIVE_TITLE)
    print(f"updated {args.company} / {args.role} -> {args.stage}")


def cmd_record_event(args):
    rows = read_table(ACTIVE_PATH)
    row = find_row(rows, args.company, args.role)
    if row is None:
        print(f"error: {args.company} / {args.role} not found in tracker.md", file=sys.stderr)
        sys.exit(1)
    row["Next Action"] = args.event
    row["Next Action Date"] = args.date
    row["Last Activity"] = today()
    write_table(ACTIVE_PATH, rows, ACTIVE_TITLE)
    print(f"recorded event for {args.company} / {args.role}: {args.event} ({args.date})")


def cmd_close(args):
    rows = read_table(ACTIVE_PATH)
    row = find_row(rows, args.company, args.role)
    if row is None:
        print(f"error: {args.company} / {args.role} not found in tracker.md", file=sys.stderr)
        sys.exit(1)
    rows.remove(row)
    write_table(ACTIVE_PATH, rows, ACTIVE_TITLE)

    closed_rows = read_table(CLOSED_PATH)
    closed_rows.append(row)
    write_table(CLOSED_PATH, closed_rows, CLOSED_TITLE)

    notes_dir = Path("opportunity") / args.company / args.role
    notes_dir.mkdir(parents=True, exist_ok=True)
    notes_path = notes_dir / "notes.md"
    with notes_path.open("a") as f:
        f.write(f"\n- **Closed ({today()}):** {args.reason}\n")

    print(f"closed {args.company} / {args.role}: {args.reason}")


def cmd_list(args):
    path = CLOSED_PATH if args.closed else ACTIVE_PATH
    title = CLOSED_TITLE if args.closed else ACTIVE_TITLE
    rows = read_table(path)
    print(serialize_table(rows, title))


def build_parser():
    parser = argparse.ArgumentParser(description="Manage tracker.md / tracker_closed.md")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("company")
    p_add.add_argument("role")
    p_add.add_argument("--stage", required=True)
    p_add.add_argument("--next-action", default="")
    p_add.add_argument("--next-action-date", default="")
    p_add.add_argument("--last-activity")
    p_add.set_defaults(func=cmd_add)

    p_update = sub.add_parser("update-status")
    p_update.add_argument("company")
    p_update.add_argument("role")
    p_update.add_argument("--stage", required=True)
    p_update.add_argument("--next-action")
    p_update.add_argument("--next-action-date")
    p_update.add_argument("--last-activity")
    p_update.set_defaults(func=cmd_update_status)

    p_event = sub.add_parser("record-event")
    p_event.add_argument("company")
    p_event.add_argument("role")
    p_event.add_argument("--event", required=True)
    p_event.add_argument("--date", required=True)
    p_event.set_defaults(func=cmd_record_event)

    p_close = sub.add_parser("close")
    p_close.add_argument("company")
    p_close.add_argument("role")
    p_close.add_argument("--reason", required=True)
    p_close.set_defaults(func=cmd_close)

    p_list = sub.add_parser("list")
    p_list.add_argument("--closed", action="store_true")
    p_list.set_defaults(func=cmd_list)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m unittest tools/test_tracker.py -v`
Expected: PASS — all 10 tests

- [ ] **Step 5: Commit**

```bash
git add tools/tracker.py tools/test_tracker.py
git commit -m "Add tracker.py: sole writer of tracker.md / tracker_closed.md"
```

---

## Task 3: Carry Over `gmail_extract.py`

**Files:**
- Create: `tools/gmail_extract.py` (copied from `~/code/job-search/tools/gmail_extract.py`)

**Interfaces:**
- Consumes: nothing from this repo.
- Produces: `python3 tools/gmail_extract.py <thread_json_file> [--after YYYY-MM-DD] [--latest N]`, used later by `morning-scan` (Task 13).

- [ ] **Step 1: Copy the file verbatim**

```bash
cp ~/code/job-search/tools/gmail_extract.py tools/gmail_extract.py
```

- [ ] **Step 2: Verify it contains no personal facts**

Run: `grep -niE 'jim|krygowski' tools/gmail_extract.py`
Expected: no matches (exit code 1). This script parses generic Gmail thread JSON — if it matches, remove the personal reference before continuing, since this file lives in the engine zone.

- [ ] **Step 3: Verify it still runs**

Run: `python3 tools/gmail_extract.py --help`
Expected: prints usage text, exit code 0

- [ ] **Step 4: Commit**

```bash
git add tools/gmail_extract.py
git commit -m "Carry over gmail_extract.py from job-search (stdlib-only, no changes needed)"
```

---

## Task 4: `build-profile` Skill

**Files:**
- Create: `.claude/skills/build-profile/SKILL.md`

**Interfaces:**
- Consumes: `career/resume/master_resume.md` (optional, if present).
- Produces: `career/profile.md`. Read by `define-trajectory` (Task 5), `career-coach` (Task 12), `score-opportunity` (Task 7), `tailor-resume` (Task 8), `interview-prep` (Task 10).

- [ ] **Step 1: Write the skill file**

```markdown
---
name: build-profile
description: Use when a user needs to create or update their career profile — either as part of first-time bootstrap or any time their background needs re-capturing. Guides a conversation about career history, best/worst jobs and bosses, and produces career/profile.md.
---

# Build Profile

## Purpose

Produce `career/profile.md` — the source of truth for who this person is
professionally. Read by every other skill in this system (`career-coach`,
`tailor-resume`, `score-opportunity`, `define-trajectory`, etc.), so it
must be concrete, not vague.

## Session Start

1. Check whether `career/profile.md` already exists.
   - If it exists, tell the user what's already captured and ask whether
     they want to add to it, correct something, or redo a section — don't
     silently overwrite.
   - If it doesn't exist, this is a first-time build.
2. Ask whether they have an existing resume to seed from
   (`career/resume/master_resume.md`, or a resume they can paste/upload).
   If yes, read it and draft an initial pass at the sections below for
   them to correct rather than starting from a blank page. If no, build
   the sections from conversation alone.

## What to Capture

Work through these one at a time — don't dump all the questions at once:

1. **Career history** — company by company: what they did, what changed,
   why they moved on.
2. **Best job, and why.** What specifically made it the best — the work,
   the people, the autonomy, the growth, the outcome?
3. **Worst job, and why.** Same level of specificity.
4. **Best boss, and why.** What did that person actually do that made
   them good to work for?
5. **Worst boss, and why.**
6. **Patterns.** After all five, name back to the user what you're
   noticing — a real pattern across their answers, not a generic
   observation. This feeds `define-trajectory` directly.

## Output

Write `career/profile.md` with clear headers matching the sections above.
Use the user's own words and specifics where possible — this file is
read by skills that draft resumes and cover letters, and vague profile
content produces vague drafts.

## Guardrails

- Never invent career history the user didn't state. If a resume you're
  seeding from has a gap or unclear detail, ask rather than assume.
- One question at a time — follow up on interesting answers before
  moving to the next section.
```

- [ ] **Step 2: Verify frontmatter parses**

Run: `python3 -c "
import re
text = open('.claude/skills/build-profile/SKILL.md').read()
m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
assert m, 'no frontmatter block found'
assert 'name: build-profile' in m.group(1)
assert 'description:' in m.group(1)
print('ok')
"`
Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/build-profile/SKILL.md
git commit -m "Add build-profile skill"
```

---

## Task 5: `define-trajectory` Skill

**Files:**
- Create: `.claude/skills/define-trajectory/SKILL.md`

**Interfaces:**
- Consumes: `career/profile.md` (optional but expected).
- Produces: `career/trajectory.md` with a `Last reviewed:` field. Read by `score-opportunity` (Task 7), `career-coach` (Task 12), `interview-prep` (Task 10).

- [ ] **Step 1: Write the skill file**

```markdown
---
name: define-trajectory
description: Use when a user needs to define or revisit their target role and career direction — as part of first-time bootstrap, or any time real feedback (an interview outcome, a networking conversation, a "golden question" conversation) suggests their must-haves have changed. Builds or updates career/trajectory.md in the Mnookin Two-Pager format.
---

# Define Trajectory

## Purpose

Produce or update `career/trajectory.md` — the target-role definition
used by `score-opportunity`, `career-coach`, and `tailor-resume`. Shaped
as a "Mnookin Two-Pager" (from *Never Search Alone*, Phyl Terry): a
concise, honest pitch document, not an internal wishlist. It should be
something the user could actually hand to a recruiter or a contact.

## Session Start

1. Check whether `career/trajectory.md` exists.
   - **Doesn't exist → initial mode.** Build it from scratch.
   - **Exists → revisit mode.** Summarize it back to the user, ask what's
     changed. Update in place — don't rebuild from scratch. Update the
     `Last reviewed:` field when done, regardless of how much changed.
2. Read `career/profile.md` first if it exists — trajectory should build
   on the patterns identified there, not ignore them.

## Sections (Mnookin Two-Pager shape)

- **Last reviewed:** `<date>`
- **What I love doing** — the work itself, specifically.
- **What I hate doing** — equally specific.
- **Must-haves** — non-negotiable for the next role.
- **Must-nots** — dealbreakers.
- **Short-term goal (next role)** — what the next role needs to be.
- **Long-term goal (3-5 years)** — where this is heading.
- **Strengths** — grounded in `career/profile.md`, not generic.
- **Weaknesses / stretch areas** — honest, not softened.

## Initial Mode — Conversation Guide

Ask one at a time, in the order above. For must-haves/must-nots, push for
specificity — "good culture" is not a must-have, "reports to the CEO or
founder, not another engineering exec" is.

For the short-term goal, do an honest stretch assessment: given
`career/profile.md`, is the target role a lateral move, a stretch, or a
reach? Say so directly. If it's a stretch or reach, talk through how to
position existing experience or what gap needs filling before or during
the search.

## Revisit Mode — Conversation Guide

Ask what prompted the revisit (or say what you noticed, if you're the one
triggering it — a `career-coach` staleness flag, or feedback from a
recent interview/conversation). Go section by section only where
something might have changed — don't re-litigate settled sections.
Explicitly ask the Never Search Alone "golden question" if the user has
had any recent networking or informational conversations: *"Based on
what [contact] told you, would you approach this search any differently
now?"*

## Guardrails

- Stay honest, not aspirational — the stretch/gap assessment only works
  if it isn't softened for comfort.
- Don't silently overwrite in revisit mode — confirm changes before
  writing.
```

- [ ] **Step 2: Verify frontmatter parses**

Run: `python3 -c "
import re
text = open('.claude/skills/define-trajectory/SKILL.md').read()
m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
assert m and 'name: define-trajectory' in m.group(1) and 'description:' in m.group(1)
print('ok')
"`
Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/define-trajectory/SKILL.md
git commit -m "Add define-trajectory skill (initial + revisit modes)"
```

---

## Task 6: `bootstrap` Skill

**Files:**
- Create: `.claude/skills/bootstrap/SKILL.md`

**Interfaces:**
- Consumes: `build-profile` skill (Task 4), `define-trajectory` skill (Task 5).
- Produces: the first-time-user entry point referenced by `CLAUDE.md` (Task 1).

- [ ] **Step 1: Write the skill file**

```markdown
---
name: bootstrap
description: Use when a new user is setting up this system for the first time, or when career/profile.md and career/trajectory.md don't exist yet. Runs a Python preflight check, then build-profile, then define-trajectory in sequence.
---

# Bootstrap

## Purpose

First-time setup orchestrator. Gets a new user from a fresh `git clone`
to a working `career/profile.md` and `career/trajectory.md`.

## Steps

1. **Preflight check.** Run:
   ```
   python3 --version
   ```
   If this fails (command not found) or reports a version below 3.9, stop
   and tell the user Python 3 is required, with install instructions:
   - macOS: `brew install python3` (or the installer at python.org)
   - Linux: use your distribution's package manager (e.g.
     `apt install python3` on Debian/Ubuntu)
   - Windows: install from python.org, checking "Add to PATH"

   Don't attempt to install Python automatically — this is a machine-wide
   change outside this repo, and the user should control it. Once they
   confirm Python is available, re-run the check before continuing.

2. **Check existing state.**
   - If `career/profile.md` and `career/trajectory.md` both already
     exist, tell the user setup already looks complete and ask if they
     want to revisit either one (hand off to `build-profile` or
     `define-trajectory` directly) rather than re-running bootstrap.
   - If `career/profile.md` doesn't exist, continue to step 3.
   - If `career/profile.md` exists but `career/trajectory.md` doesn't,
     skip to step 4.

3. **Run `build-profile`.** Don't proceed to step 4 until
   `career/profile.md` is written.

4. **Run `define-trajectory`** (initial mode, since `career/trajectory.md`
   doesn't exist yet).

5. **Wrap up.** Tell the user what was created and point them at
   `score-opportunity` as the natural next step — pasting in a JD to
   evaluate.
```

- [ ] **Step 2: Verify frontmatter parses**

Run: `python3 -c "
import re
text = open('.claude/skills/bootstrap/SKILL.md').read()
m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
assert m and 'name: bootstrap' in m.group(1) and 'description:' in m.group(1)
print('ok')
"`
Expected: `ok`

- [ ] **Step 3: Manual dry-run**

Start a Claude Code session in this repo with no `career/` directory
present, invoke the `bootstrap` skill, and confirm: it checks
`python3 --version` first, then walks into `build-profile`, then
`define-trajectory`, producing both files by the end.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/bootstrap/SKILL.md
git commit -m "Add bootstrap skill: preflight check + build-profile + define-trajectory"
```

---

## Task 7: `score-opportunity` Skill

**Files:**
- Create: `.claude/skills/score-opportunity/SKILL.md`

**Interfaces:**
- Consumes: `career/trajectory.md`, `career/profile.md`, `python3 tools/tracker.py add <company> <role> --stage ... [--next-action ...] [--next-action-date ...]` (Task 2).
- Produces: `opportunity/<Company>/<Role>/jd.md`, a new row in `tracker.md`. Read by `tailor-resume` (Task 8), `company-research` (Task 9), `interview-prep` (Task 10).

- [ ] **Step 1: Write the skill file**

```markdown
---
name: score-opportunity
description: Use when a user pastes a job description to evaluate, or wants to re-score an opportunity already in the pipeline. Scores against career/trajectory.md, creates the opportunity folder, and adds/updates the tracker row via tools/tracker.py.
---

# Score Opportunity

## Purpose

Turn a job description into a scored, tracked opportunity.

## Session Start

Read `career/trajectory.md` (must-haves, must-nots, short-term goal) and
`career/profile.md`. If `career/trajectory.md` doesn't exist yet, tell the
user to run `bootstrap` or `define-trajectory` first — scoring without a
trajectory to score against isn't meaningful.

## New Opportunity (JD pasted in chat)

1. Identify Company and Role from the JD.
2. Check whether `opportunity/<Company>/<Role>/` already exists. If so,
   treat this as a re-score (below) instead.
3. Score the JD against `trajectory.md`'s must-haves and must-nots
   explicitly — go through each one and say whether the JD satisfies it,
   contradicts it, or doesn't say. Don't produce a single vague score
   without this breakdown.
4. Create `opportunity/<Company>/<Role>/jd.md` with the full JD text plus
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

Read the existing `opportunity/<Company>/<Role>/jd.md` and
`opportunity/<Company>/<Role>/notes.md`, re-run the must-have/must-not
breakdown against the current `career/trajectory.md` (useful right after
a trajectory revisit), and append the updated scoring to `jd.md` with
today's date rather than overwriting the original scoring.

## Guardrails

- Every score must cite the specific trajectory criterion it's based on.
  No unsupported "this feels like a good fit."
- Never call `tracker.py update-status` or edit `tracker.md` directly
  from this skill — use `add` for new opportunities only. Stage changes
  after this point belong to other skills (`interview-review`,
  `morning-scan`) or a direct user request.
```

- [ ] **Step 2: Verify frontmatter parses and the tracker command referenced matches the real CLI**

Run: `python3 -c "
import re
text = open('.claude/skills/score-opportunity/SKILL.md').read()
m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
assert m and 'name: score-opportunity' in m.group(1)
assert 'tools/tracker.py add' in text
"`
Then: `python3 tools/tracker.py add --help`
Expected: first command prints nothing (assertions pass); second prints
usage including `--stage`, `--next-action`, `--next-action-date`,
confirming the skill's example call matches real flags.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/score-opportunity/SKILL.md
git commit -m "Add score-opportunity skill"
```

---

## Task 8: `tailor-resume` Skill

**Files:**
- Create: `.claude/skills/tailor-resume/SKILL.md`

**Interfaces:**
- Consumes: `career/resume/master_resume.md`, `career/profile.md`, `opportunity/<Company>/<Role>/jd.md` (Task 7).
- Produces: `opportunity/<Company>/<Role>/resume.md`, `opportunity/<Company>/<Role>/cover_letter.md`.

- [ ] **Step 1: Write the skill file**

```markdown
---
name: tailor-resume
description: Use when a user wants a resume and/or cover letter tailored to a specific opportunity already in the pipeline. Reads career/resume/master_resume.md and the opportunity's jd.md, writes resume.md and cover_letter.md into that opportunity's folder.
---

# Tailor Resume

## Purpose

Produce `opportunity/<Company>/<Role>/resume.md` and
`opportunity/<Company>/<Role>/cover_letter.md` from the master resume and
the specific JD — without inventing anything not in the master resume or
`career/profile.md`.

## Session Start

Read `career/resume/master_resume.md`, `career/profile.md`, and the
target opportunity's `jd.md`. If any of these don't exist, tell the user
what's missing rather than improvising around the gap (a missing `jd.md`
means `score-opportunity` hasn't been run yet; no master resume means
`build-profile` hasn't produced one).

## Resume

1. Identify the JD's key requirements and keywords.
2. Select and reorder relevant experience from the master resume — do not
   add experience, skills, or accomplishments that aren't in the master
   resume or something the user states directly in this conversation.
3. Where the JD wants something the master resume doesn't clearly show,
   say so to the user rather than papering over it — ask if there's
   relevant experience missing from the master resume, or flag it as a
   real gap.
4. Write `opportunity/<Company>/<Role>/resume.md`. ATS-friendly: no
   tables, no columns, no graphics.
5. Include a brief keyword-gap note at the end of your chat response (not
   the file) — what the JD asks for that the tailored resume doesn't
   fully cover.

## Cover Letter

Write `opportunity/<Company>/<Role>/cover_letter.md`, connecting specific
experience from the master resume to the company's stated needs in the
JD. Ask the user if there's a specific angle they want emphasized before
drafting.

## Guardrails

- Never invent experience, metrics, or accomplishments. Every claim must
  trace to `master_resume.md`, `career/profile.md`, or something the user
  says directly.
- This skill never sends anything — it only writes files.
```

- [ ] **Step 2: Verify frontmatter parses**

Run: `python3 -c "
import re
text = open('.claude/skills/tailor-resume/SKILL.md').read()
m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
assert m and 'name: tailor-resume' in m.group(1) and 'description:' in m.group(1)
print('ok')
"`
Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/tailor-resume/SKILL.md
git commit -m "Add tailor-resume skill"
```

---

## Task 9: `company-research` Skill

**Files:**
- Create: `.claude/skills/company-research/SKILL.md`

**Interfaces:**
- Consumes: `career/trajectory.md`, `opportunity/<Company>/<Role>/` (Task 7).
- Produces: an appended `## Company Research (<date>)` section in `opportunity/<Company>/<Role>/notes.md`.

- [ ] **Step 1: Write the skill file**

```markdown
---
name: company-research
description: Use when a user wants research on a target company — for a new opportunity or ahead of an interview. Writes cited findings into that opportunity's notes.md.
---

# Company Research

## Purpose

Research a company relevant to a specific opportunity and record findings
in `opportunity/<Company>/<Role>/notes.md` with sources attached.

## Session Start

Confirm which opportunity this research is for. If
`opportunity/<Company>/<Role>/` doesn't exist yet, ask whether to run
`score-opportunity` first — but proceed anyway if the user wants to look
before pasting the JD.

## What to Research

- Recent news, funding, leadership changes
- Product/market position and how the role's function fits into it
- Anything relevant to the specific role — team size, reporting line,
  recent org changes
- Anything relevant to the person's must-haves/must-nots from
  `career/trajectory.md` (e.g. if remote-vs-hybrid is a must-have, look
  for signal on that specifically)

## Output

Append to `opportunity/<Company>/<Role>/notes.md` under a
`## Company Research (<date>)` heading. Every finding gets a source (URL,
or "user's own knowledge" if it came from the conversation, or "my
inference" if you're inferring rather than citing something concrete —
label it explicitly, don't blend it in as fact).
```

- [ ] **Step 2: Verify frontmatter parses**

Run: `python3 -c "
import re
text = open('.claude/skills/company-research/SKILL.md').read()
m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
assert m and 'name: company-research' in m.group(1) and 'description:' in m.group(1)
print('ok')
"`
Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/company-research/SKILL.md
git commit -m "Add company-research skill"
```

---

## Task 10: `interview-prep` Skill

**Files:**
- Create: `.claude/skills/interview-prep/SKILL.md`

**Interfaces:**
- Consumes: `opportunity/<Company>/<Role>/jd.md`, `notes.md`, `contacts.md` (Task 7), `career/trajectory.md`.
- Produces: a briefing in chat, optionally appended to `notes.md` under `## Interview Prep (<date>)`.

- [ ] **Step 1: Write the skill file**

```markdown
---
name: interview-prep
description: Use when a user has an upcoming interview or call and wants a prep briefing. Reads the opportunity's jd.md, notes.md, contacts.md, and career/trajectory.md to produce likely questions and talking points.
---

# Interview Prep

## Purpose

Produce a prep briefing ahead of a specific call or interview.

## Session Start

Identify which opportunity and which stage of interview this is for.
Read `opportunity/<Company>/<Role>/jd.md`, `notes.md`, `contacts.md`, and
`career/trajectory.md`.

## Briefing Contents

1. **Who they're likely talking to** — from `contacts.md`, plus what's
   known about that person's role and priorities from `notes.md`.
2. **Likely questions** — grounded in the JD and this stage of the
   process (a recruiter screen asks different things than a CEO round).
3. **Suggested talking points** — drawn from `career/profile.md` and
   `master_resume.md`, matched to what this specific interviewer likely
   cares about. Don't invent accomplishments to fit — if there's a gap
   between what they'll probably ask and what the user has to offer, name
   it and help them think through how to answer honestly.
4. **Questions the user should ask** — grounded in `career/trajectory.md`
   must-haves/must-nots that this stage of the process can actually
   surface information about (e.g. reporting line, team structure).

## Output

Write the briefing into the chat response. If the user wants it saved,
append it to `opportunity/<Company>/<Role>/notes.md` under an
`## Interview Prep (<date>)` heading.
```

- [ ] **Step 2: Verify frontmatter parses**

Run: `python3 -c "
import re
text = open('.claude/skills/interview-prep/SKILL.md').read()
m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
assert m and 'name: interview-prep' in m.group(1) and 'description:' in m.group(1)
print('ok')
"`
Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/interview-prep/SKILL.md
git commit -m "Add interview-prep skill"
```

---

## Task 11: `interview-review` Skill

**Files:**
- Create: `.claude/skills/interview-review/SKILL.md`

**Interfaces:**
- Consumes: a call transcript, `summarize-call` command (Task 14, optional pre-step), `python3 tools/tracker.py update-status <company> <role> --stage ... [--next-action ...] [--next-action-date ...]` (Task 2).
- Produces: an appended `## Interview Review (<date>)` section in `notes.md`, saved transcript in `opportunity/<Company>/<Role>/transcripts/`, an updated tracker row.

- [ ] **Step 1: Write the skill file**

```markdown
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
   `opportunity/<Company>/<Role>/notes.md`.
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
```

- [ ] **Step 2: Verify frontmatter parses and the tracker command matches the real CLI**

Run: `python3 -c "
import re
text = open('.claude/skills/interview-review/SKILL.md').read()
m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
assert m and 'name: interview-review' in m.group(1)
assert 'tools/tracker.py update-status' in text
"`
Then: `python3 tools/tracker.py update-status --help`
Expected: first command prints nothing; second prints usage including
`--stage`, `--next-action`, `--next-action-date`.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/interview-review/SKILL.md
git commit -m "Add interview-review skill"
```

---

## Task 12: Port `career-coach` Skill

**Files:**
- Create: `.claude/skills/career-coach/SKILL.md` (ported from `~/.claude/skills/career-coach/SKILL.md`)
- Create: `.claude/skills/career-coach/research.md` (copied verbatim)

**Interfaces:**
- Consumes: `career/profile.md`, `career/trajectory.md` (its `Last reviewed:` field), `tracker.md`, `opportunity/*/notes.md`.
- Produces: no files — an interactive coaching session.

**Why this is a port, not a fresh write:** the existing skill's coaching
frameworks (Schein's Anchors, Opportunity Fit, SDT, Ibarra, Career
Capital, Regret Minimization, Ikigai) and their evidence-quality
annotations are already validated content — don't rewrite them. What
needs to change is everything that hardcodes Jim-specific facts or old
file paths, per the engine/data separation (§3 of the spec).

- [ ] **Step 1: Copy the source file as a starting point**

```bash
mkdir -p .claude/skills/career-coach
cp ~/.claude/skills/career-coach/SKILL.md .claude/skills/career-coach/SKILL.md
cp ~/.claude/skills/career-coach/research.md .claude/skills/career-coach/research.md
```

- [ ] **Step 2: Replace the hardcoded bio in the Overview section**

Find:
```
You are Jim Krygowski's career coach. Jim is an engineering executive (25+ years, Boston MA) targeting CTO, VP Engineering, or Senior Director roles. He was laid off from Jellyfish in May 2026 when a new head of engineering restructured the org; his portfolio was deprioritized. He is actively searching.
```

Replace with:
```
You are this user's career coach. Read `career/profile.md` and
`career/trajectory.md` before doing anything else — they hold the bio,
career history, and target-role facts this session needs. Don't assume
anything about the user beyond what's written there or what they tell
you directly in conversation.
```

- [ ] **Step 3: Replace the Session Start Protocol's hardcoded paths**

Find:
```
1. **Read the pipeline:** `/Users/mizuekrygowski/code/job-search/companies/` and `/Users/mizuekrygowski/code/job-search/00_Admin/applications.csv`
2. **Read memory context:** Check `/Users/mizuekrygowski/.claude/projects/-Users-mizuekrygowski-code-job-search/memory/project_job_search.md` for current pipeline state
3. **Confirm what Jim wants from this session** before diving in — analysis, decision support, priority clarification, or something else
```

Replace with:
```
1. **Read the pipeline:** `tracker.md` (and `opportunity/<Company>/<Role>/notes.md` for any opportunity under discussion).
2. **Read `career/profile.md` and `career/trajectory.md`.** Check
   `trajectory.md`'s `Last reviewed:` date — if it's more than 6 weeks
   old, flag this to the user before going further and offer to run
   `define-trajectory` in revisit mode.
3. **Confirm what the user wants from this session** before diving in —
   analysis, decision support, priority clarification, or something else.
```

- [ ] **Step 4: Replace "Jim's Known Preferences" section**

Find the entire section starting with:
```
## Jim's Known Preferences (as of June 2026)

- Prefers **hybrid** over fully remote
- Prefers **reporting to CEO or founder** over reporting to another engineering exec
- Wants **full VP Eng or CTO scope** — not applications-only or segment roles
- Has done large-org (55 eng, CRD) and growth-stage (25 eng, Jellyfish) — comfortable at both
- AI infrastructure work at Jellyfish is a differentiator; wants to continue in that direction
- **Not anchored to EdTech or any specific vertical** — domain is secondary to problem quality
```

Replace with:
```
## Known Preferences

Don't hardcode preferences here — they live in `career/trajectory.md`
(must-haves / must-nots) and evolve as the search progresses. Read that
file fresh each session rather than relying on what you remember from a
prior one.
```

- [ ] **Step 5: Replace remaining "Jim" references in prose with "the user"**

Run: `grep -n '\bJim\b' .claude/skills/career-coach/SKILL.md`

For each match outside the sections already replaced in Steps 2-4,
replace `Jim` with `the user` (e.g. in the Coaching Posture and framework
usage-guidance sections). Preserve everything else verbatim — the
frameworks and their evidence annotations don't change.

- [ ] **Step 6: Verify no hardcoded personal facts or old paths remain**

Run: `grep -niE 'jim|krygowski|/code/job-search/|applications\.csv|companies/' .claude/skills/career-coach/SKILL.md`
Expected: no matches (exit code 1)

- [ ] **Step 7: Verify frontmatter still parses**

Run: `python3 -c "
import re
text = open('.claude/skills/career-coach/SKILL.md').read()
m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
assert m and 'name: career-coach' in m.group(1) and 'description:' in m.group(1)
print('ok')
"`
Expected: `ok`

- [ ] **Step 8: Commit**

```bash
git add .claude/skills/career-coach/
git commit -m "Port career-coach skill: read profile/trajectory instead of hardcoded facts"
```

---

## Task 13: Port `morning-scan` Skill

**Files:**
- Create: `.claude/skills/morning-scan/SKILL.md` (ported from `~/.claude/skills/morning-scan/SKILL.md`)
- Create: `career/job_alert_sources.md`

**Interfaces:**
- Consumes: `tracker.md`, `opportunity/*/contacts.md` (built up over time by `score-opportunity`/manual edits), `career/job_alert_sources.md`, `tools/gmail_extract.py` (Task 3), `python3 tools/tracker.py record-event <company> <role> --event ... --date ...` (Task 2).
- Produces: an updated tracker row per new calendar event found; a chat summary.

**Why this needs more than a path swap:** the existing skill hardcodes
the "Pipeline Contact List" and job-alert sender addresses directly in
the skill file — that's personal data living in the engine zone, which
contradicts the engine/data separation in §3 of the spec more directly
than `career-coach` did. This port moves that data out.

- [ ] **Step 1: Copy the source file as a starting point**

```bash
mkdir -p .claude/skills/morning-scan
cp ~/.claude/skills/morning-scan/SKILL.md .claude/skills/morning-scan/SKILL.md
```

- [ ] **Step 2: Create `career/job_alert_sources.md`**

This replaces the hardcoded ZenSearch/LinkedIn sender addresses and
filter criteria in the skill file. Seed it with a template the user fills
in during their own setup (the actual addresses are personal/account-
specific and get migrated in, not authored here):

```markdown
# Job Alert Sources

List the email senders that deliver job alerts, and what to filter for.
`morning-scan` reads this file to build its Tier 2 search.

## Example format

- **Source name:** ZenSearch
  **Sender pattern:** `from:example@zensearch.jobs`
  **Lookback:** `newer_than:2d`
  **Filter for:** title/company/location/comp matching
  `career/trajectory.md` must-haves

(Replace this example with real sources during setup.)
```

- [ ] **Step 3: Replace Tier 1 (Pipeline Emails) to read contacts dynamically**

Find:
```
Search for new messages from all active pipeline contacts in the last 24 hours:

```
from:(louis@boredm.com OR laura.cain@fiveelms.com OR lauren.clausen@altana.ai) newer_than:1d
```
```

Replace with:
```
Build the contact list dynamically rather than using a fixed list: read
`tracker.md` for active opportunities, then read each corresponding
`opportunity/<Company>/<Role>/contacts.md` for that opportunity's known
contact emails. Search for new messages from all of them in the last 24
hours:

```
from:(<contact1> OR <contact2> OR ...) newer_than:1d
```
```

- [ ] **Step 4: Replace Tier 2 (Job Alert Feeds) to read from the data file**

Find:
```
## Tier 2 — Job Alert Feeds
Run both in parallel with Tier 1:

- **ZenSearch:** `from:amy@zensearch.jobs newer_than:2d`
- **LinkedIn:** `from:(jobalerts-noreply@linkedin.com OR jobs-listings@linkedin.com OR jobs-noreply@linkedin.com) newer_than:2d` — emails route to `jimkski+linkedin@gmail.com`

For ZenSearch: extract each job listing (title, company, location, comp). Flag any that match Jim's target profile — CTO/VPE/Sr Dir, B2B SaaS, Greater Boston or remote-friendly, $250K+ base, manages through managers. Skip the rest.

For LinkedIn: extract job titles and companies. Apply same filter.
```

Replace with:
```
## Tier 2 — Job Alert Feeds

Read `career/job_alert_sources.md` for the configured sources and run
each in parallel with Tier 1. For each source, extract job listings
(title, company, location, comp) and flag any that match the must-haves
in `career/trajectory.md`. Skip the rest.
```

- [ ] **Step 5: Update Tier 3 (Calendar) to persist findings via `tracker.py`**

Find:
```
## Tier 3 — Calendar
List events from today through end of the week. Flag:
- Any job search calls or interviews
- Deadlines or follow-up windows that are closing
- Conflicts with expected pipeline activity
```

Replace with:
```
## Tier 3 — Calendar
List events from today through end of the week. For any event that's a
job search call/interview or a closing deadline for an opportunity in
`tracker.md`, persist it instead of only reporting it in chat:
```
python3 tools/tracker.py record-event "<Company>" "<Role>" \
  --event "<what the event is>" --date "<date>"
```
Flag any conflicts with expected pipeline activity in the summary as
well.
```

- [ ] **Step 6: Replace the applications.csv reference in the intro**

Find:
```
3. Read `00_Admin/applications.csv` (the source of truth for pipeline state — see the Job Search Project memory) so the scan is grounded in each company's current stage, last activity, and next action before pulling email/calendar.
```

Replace with:
```
3. Read `tracker.md` (the source of truth for pipeline state) so the scan is grounded in each company's current stage, last activity, and next action before pulling email/calendar.
```

- [ ] **Step 7: Remove the hardcoded "Pipeline Contact List" section**

Find the entire section starting with:
```
## Pipeline Contact List (keep current)
Update this list as the pipeline changes.

| Company | Key Contacts |
```
through the end of that table and the "Closed with no further expected
contact" line.

Delete it entirely — contacts now live per-opportunity in
`opportunity/<Company>/<Role>/contacts.md`, read dynamically per Step 3.

- [ ] **Step 8: Verify no hardcoded personal facts remain**

Run: `grep -niE 'jim|krygowski|boredm\.com|fiveelms\.com|altana\.ai|zensearch\.jobs|applications\.csv|00_Admin' .claude/skills/morning-scan/SKILL.md`
Expected: no matches (exit code 1)

- [ ] **Step 9: Verify frontmatter still parses and the tracker command matches the real CLI**

Run: `python3 -c "
import re
text = open('.claude/skills/morning-scan/SKILL.md').read()
m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
assert m and 'name: morning-scan' in m.group(1)
assert 'tools/tracker.py record-event' in text
"`
Then: `python3 tools/tracker.py record-event --help`
Expected: first command prints nothing; second prints usage including
`--event`, `--date`.

- [ ] **Step 10: Commit**

```bash
git add .claude/skills/morning-scan/SKILL.md career/job_alert_sources.md
git commit -m "Port morning-scan skill: dynamic contacts/job-alert sources, record-event persistence"
```

---

## Task 14: Port `summarize-call` Command

**Files:**
- Create: `.claude/commands/summarize-call.md` (ported from `~/code/job-search/.claude/commands/summarize-call.md`)

**Interfaces:**
- Consumes: a pasted transcript or file path, `python3 tools/tracker.py update-status <company> <role> --stage ... [--next-action ...] [--next-action-date ...]` (Task 2).
- Produces: `opportunity/<Company>/<Role>/transcripts/<Contact>_Call_<YYYY-MM-DD>.md`, an updated tracker row. Used as a pre-step by `interview-review` (Task 11).

- [ ] **Step 1: Copy the source file as a starting point**

```bash
mkdir -p .claude/commands
cp ~/code/job-search/.claude/commands/summarize-call.md .claude/commands/summarize-call.md
```

- [ ] **Step 2: Replace the file-path convention (old 5-folder layout → new opportunity layout)**

Find:
```
3. **Write the call notes file** to `04_Applications/<Company>/<Company>_<Contact>_Call_<YYYY-MM-DD>.md` using this structure:
```

Replace with:
```
3. **Write the call notes file** to `opportunity/<Company>/<Role>/transcripts/<Contact>_Call_<YYYY-MM-DD>.md` using this structure:
```

- [ ] **Step 3: Replace the applications.csv update step with a tracker.py call**

Find:
```
4. **Update `00_Admin/applications.csv`** — stage, last activity date, next action, and add a summary to the notes field.
```

Replace with:
```
4. **Update the tracker:**
   ```
   python3 tools/tracker.py update-status "<Company>" "<Role>" \
     --stage "<stage>" --next-action "<next action>" \
     --next-action-date "<date, if known>"
   ```
   Add a one-line summary to `opportunity/<Company>/<Role>/notes.md` as
   well — the tracker row itself stays to short scalar fields.
```

- [ ] **Step 4: Replace remaining "Jim" references with "the user"**

Run: `grep -n '\bJim\b' .claude/commands/summarize-call.md`

Replace each occurrence with `the user` (appears in the extraction bullet
list and the style notes).

- [ ] **Step 5: Verify no hardcoded personal facts or old paths remain**

Run: `grep -niE 'jim|krygowski|04_applications|00_admin|applications\.csv' .claude/commands/summarize-call.md`
Expected: no matches (exit code 1)

- [ ] **Step 6: Verify the tracker command referenced matches the real CLI**

Run: `grep -q 'tools/tracker.py update-status' .claude/commands/summarize-call.md && echo present`
Expected: `present`
Then: `python3 tools/tracker.py update-status --help`
Expected: usage text including `--stage`, `--next-action`, `--next-action-date`

- [ ] **Step 7: Commit**

```bash
git add .claude/commands/summarize-call.md
git commit -m "Port summarize-call command to new opportunity layout and tracker.py"
```

---

## Self-Review Notes

**Spec coverage:** §3 (Architecture) → Task 1. §4 (Repository Layout) →
Tasks 1-14 collectively produce the full tree. §5 (Data Model) →
`tracker.py`'s schema (Task 2) and `trajectory.md`'s Mnookin shape (Task
5). §6 (Skills & Commands) → Tasks 4-14, one per skill/command, new and
ported. §7 (`tracker.py`) → Task 2. §8 (Trajectory Revisit Triggers) →
Task 12 Step 3 (time-based) and Task 11 (signal-based, via
`interview-review`'s prompt to revisit). §9 (Guardrails) → Task 1 Step 2
(structural send-deny) plus instruction-level guardrails threaded through
Tasks 4, 7, 8, 9, 11. §10 (Memory & State) → no new task; explicitly out
of scope for this plan per the spec (existing Claude Code infrastructure,
nothing to build). §11 (Migration) → explicitly out of scope for this
plan per the spec. §12 (Testing & Validation) → Task 2's unit tests plus
manual dry-run steps threaded through Tasks 4-14.

**Not covered by this plan, by design:** migrating live pipeline data
from `~/code/job-search` (spec §11 defers this to after the system is
built and validated).
