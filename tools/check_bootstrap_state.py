#!/usr/bin/env python3
"""SessionStart hook: flags missing or incomplete setup before Claude's
first reply.

Checks state/career/profile.md, trajectory.md, and comp_target.md and
injects at most one note, naming which required sections are missing or
empty. This is a presence check, not a sufficiency judgment: it only
asks whether each required section has *something* written under its
heading, not whether that content is actually good. This hook runs as a
plain subprocess before Claude's turn starts -- it has no LLM available
to judge whether content is substantive, so it doesn't try. That
judgment belongs entirely to the skill that actually reads the file when
a user engages with it (build-profile/define-trajectory/offer-
negotiator's own Session Start checks), which is where it happens
correctly.

- profile.md missing or has empty/missing required sections: hard-gate
  new-user note (must lead the first reply), naming which sections.
- profile.md complete (by presence), trajectory.md complete,
  comp_target.md missing or has empty/missing required sections: soft,
  non-blocking note, naming which sections.
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


def _section_has_content(text, heading_prefix):
    """True if `text` has a "##"-level heading starting with
    heading_prefix (case-insensitive), followed by non-empty content
    before the next "##"-or-higher heading or end of string.

    This is a presence check, not a sufficiency judgment -- "is there
    anything here at all," not "is this good enough." Whether present
    content is actually substantive is a real judgment call, and this
    hook has no LLM available to make it (it runs as a plain subprocess
    before Claude's turn starts). That judgment happens exactly once,
    correctly, in the skill that actually reads the file -- not
    approximated here with a character-count threshold.

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
    return len(m.group(1).strip()) > 0


def _missing_sections(path, required_sections):
    """Returns the subset of required_sections that are missing or
    empty. A missing or unreadable file trivially returns the full
    list -- every required section is "missing" in that case."""
    if not path.exists():
        return list(required_sections)
    try:
        text = path.read_text()
    except (OSError, UnicodeDecodeError):
        return list(required_sections)
    return [s for s in required_sections if not _section_has_content(text, s)]


def _emit(context):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }))


def main():
    profile_missing = _missing_sections(PROFILE_PATH, PROFILE_REQUIRED_SECTIONS)
    if profile_missing:
        if not PROFILE_PATH.exists():
            detail = "does not exist"
        else:
            detail = "is missing: " + ", ".join(profile_missing)
        _emit(
            f"state/career/profile.md {detail}. This is a new user who "
            "has not run bootstrap yet (or started it and didn't "
            "finish). Your very first reply this session, before "
            "addressing anything else the user asked, must say so "
            "plainly and offer to run the `bootstrap` skill now."
        )
        return

    trajectory_missing = _missing_sections(TRAJECTORY_PATH, TRAJECTORY_REQUIRED_SECTIONS)
    comp_target_missing = _missing_sections(COMP_TARGET_PATH, COMP_TARGET_REQUIRED_SECTIONS)
    if not trajectory_missing and comp_target_missing:
        if not COMP_TARGET_PATH.exists():
            detail = "doesn't exist yet"
        else:
            detail = "is missing: " + ", ".join(comp_target_missing)
        _emit(
            f"state/career/comp_target.md {detail} — offer-negotiator "
            "(comp coaching/benchmarking) won't be able to ground its "
            "advice in your actual walk-away numbers until it's set up. "
            "Mention this and offer to set it up, but address whatever "
            "the user asked first."
        )


if __name__ == "__main__":
    main()
