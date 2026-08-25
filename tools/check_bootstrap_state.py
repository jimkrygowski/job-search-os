#!/usr/bin/env python3
"""SessionStart hook: flags a new user before Claude's first reply.

Checks for state/career/profile.md. If it's missing, this is a first-time
user who hasn't run `bootstrap` yet — inject that as context so Claude
leads with the bootstrap offer instead of needing to notice it on its own.
"""
import json
from pathlib import Path


def main():
    if Path("state/career/profile.md").exists():
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": (
                "state/career/profile.md does not exist. This is a new "
                "user who has not run bootstrap yet. Your very first "
                "reply this session, before addressing anything else the "
                "user asked, must say so plainly and offer to run the "
                "`bootstrap` skill now."
            ),
        }
    }))


if __name__ == "__main__":
    main()
