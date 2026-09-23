# Plugin Conversion — Design

Status: approved by Jim 2026-09-23. Implementation staged across three
PRs — see §9.

## 1. Purpose

Convert `job-search-os` from a clone-and-`cd` checkout into a Claude Code
plugin, installable from the `jimk-claude-skills` marketplace, with
personal state living outside the repo.

Three things drive this:

- **The marketplace entry already points here.** `jimk-claude-skills`
  lists `job-search-os`, but the repo has no `.claude-plugin/plugin.json`,
  so installing it yields nothing usable.
- **State has already moved out.** Personal state now lives at
  `/Users/mizuekrygowski/code/jims-2026-job-search/state`. The engine and
  the data are separate directories; the tooling has not caught up.
- **A silent failure mode exists today.** See §3.

## 2. Non-Goals

- **No dual-mode support.** After the cutover the repo works as a plugin
  only. Supporting both a plugin and a standalone checkout would require
  fallbacks in every path resolution and the operating rules to exist in
  two places without drifting — real ongoing cost for a repo with one
  known user.
- **No new repo.** The conversion happens in place, preserving history,
  name, URL, and the existing marketplace entry.
- **The send guard covers Gmail tool names only.** Browser automation
  reaching Gmail's web UI stays instruction-level, as
  `CLAUDE.md` guardrail #3 already documents. URL matching is fuzzier
  than tool-name matching and risks false positives on legitimate
  browser use.
- **No skill behavior changes.** This is a packaging and path-resolution
  change. What the skills do is out of scope.

## 3. The Bug This Fixes

`tracker.py` resolves `STATE_ROOT = Path("state")` — relative to the
current working directory — and `tracker.py:57` calls
`STATE_ROOT.mkdir(parents=True, exist_ok=True)`.

Run from a directory with no `state/`, the tools do not fail. They
**create an empty `state/` and report an empty pipeline**, with no error.
Verified empirically 2026-09-22 in a temporary directory: `tracker.py
list` printed an empty table and left a stray `state/` behind.

Today this is masked because the user always `cd`s into the repo first.
Once the plugin is loadable in a session, a `/morning-scan` fired from
any other directory reports "no opportunities" and leaves a stray
directory — a false all-clear on a live job search, with nothing to
suggest anything went wrong.

## 4. Target Layout

```
job-search-os/
  .claude-plugin/plugin.json       # name, version, description, author, license
  skills/                          # 11 tracked skills, moved from .claude/skills/
  commands/summarize-call.md       # moved from .claude/commands/
  hooks/hooks.json                 # SessionStart + PreToolUse registration
  hooks/session-start.py           # bootstrap check + operating-rules injection
  hooks/guard-send.py              # PreToolUse deny for Gmail send tools
  scripts/                         # tracker.py, score_table.py, option_value.py,
                                   # gmail_extract.py, state_path.py, tests
  instructions/operating-rules.md  # persona, guardrails, data-file map
  docs/, README.md, LICENSE        # unchanged
```

`file-unemployment-claim` exists in `.claude/skills/` on disk but is
untracked in git. It is out of scope here and stays untracked; if it is
ever committed it follows the same layout as the other skills.

## 5. State Resolution

A new `scripts/state_path.py` is imported by every tool that touches
state.

**Lookup:** read `~/.job-search-os/state-path`, a plain text file whose
first non-empty line is an absolute path to the state root.

**Failure behavior:** if the pointer file is missing, empty, or names a
directory that does not exist, the tool writes a message naming the
expected pointer path and the resolved value, and exits non-zero. It
never creates the state directory, and never falls back to `./state`.

**Removal:** the `STATE_ROOT.mkdir(parents=True, exist_ok=True)` call in
`tracker.py` is deleted. Creating the state tree becomes `bootstrap`'s
job, which already owns first-run setup.

This choice was made over an environment variable and over a symlink.
The pointer file needs no Claude Code cooperation, no shell
configuration, and is inspectable with `cat` and editable with any
editor. A `settings.json` `env` block was considered and rejected:
whether `settings.json` supports a top-level `env` key was not verified,
and the mechanism is heavier than the problem.

## 6. Path References

The two kinds of reference are handled differently, and only one
requires rewriting.

**`tools/` — rewritten.** 33 occurrences across 12 files become
`${CLAUDE_PLUGIN_ROOT}/scripts/`. These are literal shell commands the
agent runs; a stale one fails loudly with "no such file," so the failure
mode is safe. The count is the completeness check for PR 2.

**`state/` — not rewritten.** 87 occurrences across 14 files stay as
they are. `state/` is treated as a *logical* prefix, and
`instructions/operating-rules.md` binds it to the resolved absolute root:
the SessionStart hook resolves the pointer file and states the real path
in the injected context, so `state/career/profile.md` in a skill means
`<resolved root>/career/profile.md`.

Rewriting all 87 was considered and rejected. It is 87 chances to
introduce an error in prose that no test covers, for no gain — the
binding has to be explained in the operating rules regardless, and once
it is, the literal prefix is already correct. It also keeps the skills
readable: `state/career/profile.md` says more to a human reader than an
interpolated variable would.

Counted 2026-09-23.

**Consequence for failure modes.** Because skills express state paths as
prose the agent resolves rather than as commands, a broken binding does
not fail loudly the way a bad `tools/` path does. This is why §5
requires the tools themselves to resolve independently through
`state_path.py` and exit non-zero on a bad pointer: the deterministic
layer is what catches misconfiguration, not the prose.

## 7. Operating Rules, Split Two Ways

**In the plugin:** `instructions/operating-rules.md` holds the persona,
the three guardrails, the data-file map, and the bootstrap first-reply
rule — the content currently in `CLAUDE.md`. The SessionStart hook reads
it, JSON-escapes it, and emits it as `additionalContext`. This is the
mechanism `superpowers` uses to deliver `using-superpowers`, and the
mechanism `check_bootstrap_state.py` already uses for its bootstrap note.
Shipping in the plugin means updates reach every install.

**Local:** a thin `CLAUDE.md` remains in the state directory for
setup-specific overrides. Nothing is planned for it initially; it exists
so there is an obvious place for local divergence that will not be
overwritten by a plugin update.

**Install scope:** the plugin installs at **project scope** in the state
directory, not user scope. A job-search persona injected into every
session — including unrelated development work — is wrong. Project scope
means the plugin loads when Claude starts in the state directory and
nowhere else, which is also the "go to the directory and it recognizes"
behavior the user asked for.

## 8. Send Guard

`hooks/guard-send.py`, registered on `PreToolUse`, returns
`permissionDecision: "deny"` for:

- `mcp__claude_ai_Gmail__send_message`
- `mcp__claude_ai_Gmail__reply`
- `mcp__claude_ai_Gmail__forward`

This replaces the `permissions.deny` block in `.claude/settings.json`,
which cannot ship in a plugin. The hook is strictly stronger: the current
deny-list protects only this machine, while the hook protects every
install.

## 9. Implementation Stages

Each stage is a separate PR. Work happens in a git worktree so the
user's working copy keeps running the current version throughout, and
the cutover is a merge rather than a window of brokenness.

**PR 1 — state resolution.** Add `state_path.py` and the pointer file
contract; remove the silent `mkdir`; update the tools to resolve through
it. Layout untouched, tools stay in `tools/`. The system keeps working
exactly as it does now. This stage is independently valuable: it removes
the §3 bug whether or not the rest proceeds, and it unblocks deleting the
duplicate state copy at `~/code/job-search-os/state`.

**PR 2 — layout and manifest.** The cutover. `git mv` for the file moves
so history follows, add `plugin.json`, rewrite the 33 `tools/` references
per §6, add `hooks/hooks.json`. After this, clone-and-`cd` no longer
works and installation is through the marketplace.

Note the ordering constraint: the `state/` prefix binding described in
§6 is only established once `instructions/operating-rules.md` lands in
PR 3. Between PR 2 and PR 3 the skills' `state/` references rely on the
agent's working directory as they do today. PR 2 and PR 3 should
therefore land together, or PR 3 should follow immediately.

**PR 3 — operating rules and send guard.** Add
`instructions/operating-rules.md`, extend the session-start hook to
inject it, add `guard-send.py`. `CLAUDE.md` in the repo shrinks to a
pointer at the plugin.

## 10. Testing

The existing pytest suites for `tracker`, `score_table`, `option_value`,
`gmail_extract`, and `check_bootstrap_state` must stay green at every
stage. Test-driven development per `superpowers:test-driven-development`.

New coverage:

- `state_path.py`: pointer file missing; pointer file empty; pointer
  names a nonexistent directory; pointer valid. The first three assert a
  non-zero exit and that no directory was created.
- `guard-send.py`: each of the three Gmail send tool names produces a
  deny decision; an unrelated tool name does not.

**End-to-end check after PR 2**, not automated: install the plugin from
`jimk-claude-skills` into a scratch directory, point the pointer file at
real state, and run `/morning-scan`. Automated tests cannot prove the
marketplace path works.

## 11. What Breaks

`git clone && cd job-search-os` stops working at PR 2. The README's
"Getting started" section is rewritten to cover marketplace installation
and the pointer file. Anyone using the old flow either migrates or pins a
pre-conversion commit.

## 12. Open Items

None. All four design decisions — in-place restructure, pointer file,
split operating rules, PreToolUse send guard — were settled before this
document was written.
