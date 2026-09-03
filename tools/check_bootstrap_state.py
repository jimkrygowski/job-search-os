#!/usr/bin/env python3
"""SessionStart hook: flags missing or incomplete setup before Claude's
first reply.

Checks state/career/profile.md, trajectory.md, and comp_target.md and
injects at most one note. A file only counts as done if it exists AND
has every one of its required sections present with real content --
existence alone doesn't prove a workflow ran to completion (a session
that gets interrupted mid-build-profile can leave a stub file that
exists but is empty or missing whole sections).

- profile.md missing or incomplete: hard-gate new-user note (must lead
  the first reply).
- profile.md complete, trajectory.md complete, comp_target.md missing
  or incomplete: soft, non-blocking note that offer-negotiator setup
  hasn't been run.
- All three complete: no note.
"""
import json
import re
from pathlib import Path

PROFILE_PATH = Path("state/career/profile.md")
TRAJECTORY_PATH = Path("state/career/trajectory.md")
COMP_TARGET_PATH = Path("state/career/comp_target.md")

# build-profile/SKILL.md's ## Output section mandates these six headings
# (by prefix -- real headers append a descriptive suffix, e.g.
# "## Best Job: Some Company").
PROFILE_REQUIRED_SECTIONS = [
    "Career History", "Best Job", "Worst Job", "Best Boss", "Worst Boss", "Patterns",
]

# define-trajectory/SKILL.md's Mnookin Two-Pager sections, matched by
# short stable prefix so a parenthetical detail changing (e.g.
# "Long-Term Goal (3-5 years)") doesn't break this check.
TRAJECTORY_REQUIRED_SECTIONS = [
    "What I Love Doing", "What I Hate Doing", "Must-Haves", "Must-Nots",
    "Short-Term Goal", "Long-Term Goal", "Strengths", "Weaknesses",
]

# offer-negotiator/SKILL.md's ## Setup Mode -- Sections headings.
# "Last reviewed" is a one-line field, not a section with body content,
# so it's excluded here (same as trajectory.md above).
COMP_TARGET_REQUIRED_SECTIONS = [
    "BATNA", "Target / Ask Range", "Walk-Away Minimums",
    "Cash / Equity / Benefits Priority", "Equity Risk Tolerance", "Deal-Breakers",
]

# Length floor (characters, after .strip()) for a section's body text to
# count as real content rather than an empty/placeholder stub. Long
# enough to reject "TBD" or nothing at all; short enough not to reject a
# genuinely terse real answer. A judgment call, not a measured constant
# -- this is a fast, deterministic hook, not an LLM call, so it can't
# make a quality judgment, only a presence-and-length one.
MIN_SECTION_CONTENT_LENGTH = 20


def _section_has_content(text, heading_prefix):
    """True if `text` has a "##"-level heading starting with
    heading_prefix (case-insensitive), followed by at least
    MIN_SECTION_CONTENT_LENGTH characters of stripped content before the
    next "##"-or-higher heading or end of string.

    Mirrors score_table.py's _section_body regex approach (same stop-
    boundary: the next "##" heading or EOF, so a "###" sub-heading is
    correctly treated as nested content, not a terminator) but matches
    the heading by prefix rather than requiring an exact line, since
    build-profile's real headers append a descriptive suffix.
    """
    pattern = re.compile(
        rf"^##[ \t]+{re.escape(heading_prefix)}[^\n]*$(.*?)(?=^##[ \t]|\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    m = pattern.search(text)
    if m is None:
        return False
    return len(m.group(1).strip()) >= MIN_SECTION_CONTENT_LENGTH


def _file_is_complete(path, required_sections):
    if not path.exists():
        return False
    try:
        text = path.read_text()
    except (OSError, UnicodeDecodeError):
        return False
    return all(_section_has_content(text, s) for s in required_sections)


def _emit(context):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }))


def main():
    if not _file_is_complete(PROFILE_PATH, PROFILE_REQUIRED_SECTIONS):
        _emit(
            "state/career/profile.md does not exist or is incomplete. "
            "This is a new user who has not run bootstrap yet (or "
            "started it and didn't finish). Your very first reply this "
            "session, before addressing anything else the user asked, "
            "must say so plainly and offer to run the `bootstrap` skill "
            "now."
        )
        return

    if (
        _file_is_complete(TRAJECTORY_PATH, TRAJECTORY_REQUIRED_SECTIONS)
        and not _file_is_complete(COMP_TARGET_PATH, COMP_TARGET_REQUIRED_SECTIONS)
    ):
        _emit(
            "state/career/comp_target.md doesn't exist yet or is "
            "incomplete — offer-negotiator (comp coaching/benchmarking) "
            "won't be able to ground its advice in your actual "
            "walk-away numbers until it's set up. Mention this and "
            "offer to set it up, but address whatever the user asked "
            "first."
        )


if __name__ == "__main__":
    main()
