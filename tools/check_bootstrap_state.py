#!/usr/bin/env python3
"""SessionStart hook: flags missing setup before Claude's first reply.

Checks state/career/profile.md, trajectory.md, and comp_target.md and
injects at most one note:
- profile.md missing: hard-gate new-user note (must lead the first reply).
- profile.md and trajectory.md exist but comp_target.md doesn't: soft,
  non-blocking note that offer-negotiator setup hasn't been run.
- All three exist: no note.
"""
import json
from pathlib import Path


def _emit(context):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }))


def main():
    if not Path("state/career/profile.md").exists():
        _emit(
            "state/career/profile.md does not exist. This is a new "
            "user who has not run bootstrap yet. Your very first "
            "reply this session, before addressing anything else the "
            "user asked, must say so plainly and offer to run the "
            "`bootstrap` skill now."
        )
        return

    if (
        Path("state/career/trajectory.md").exists()
        and not Path("state/career/comp_target.md").exists()
    ):
        _emit(
            "state/career/comp_target.md doesn't exist yet — "
            "offer-negotiator (comp coaching/benchmarking) won't be able "
            "to ground its advice in your actual walk-away numbers until "
            "it's set up. Mention this and offer to set it up, but "
            "address whatever the user asked first."
        )


if __name__ == "__main__":
    main()
