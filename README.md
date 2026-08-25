# Job Search OS

An agentic system for running a job search with the same rigor you'd bring to any other engineering problem. Built on [Claude Code](https://claude.com/claude-code), it turns a job search into a structured pipeline — grounded in actual research rather than generic AI life-coach platitudes, and engineered with the guardrails, tests, and separation of concerns you'd expect from production software.

## Why this exists

I'm Jim Krygowski, an engineering executive with 20+ years running and scaling engineering orgs — most recently as a senior engineering leader before a layoff put me back on the market in 2026. I've hired for and sat on the other side of a lot of searches. What I haven't done is run my own job search with any real system behind it — in past searches a well organized inbox sufficed. 

While I was at Jellyfish I built myself a chief of staff agent system to help take some of toil out of my job. That experience opened my eyes to the possibilities of personal productivity systems built around an LLM. I've spoken to a lot of folks who are on the market now and have a deep appreciation for the labor that goes into the job search. I've read a lot about using chatbots to write cover letters but I wanted more. An assistant and coach capable of tackling the process end to end: candidate profile and target-role definition as real artifacts, a pipeline tracker to stay focused, opportunity based research and planning and research-grounded coaching instead of vibes. I also built this using Claude and as much as was reasonable followed good engineering practice in the construction of the agent, the building of test coverage and code review that I'd want in any software product I built or used.

I'm sharing this work in this repo for anyone who's interested in getting a boost in managing their job search. The code in this repo is 100% agent authored but it's also a fair sample of how I think about building software: what I choose to make rigorous, what I choose to leave simple, and where I draw the line between "good enough" and "worth getting right." The direction taken by Claude came from me.

If you know someone looking for CTO, VP Engineering, Head of Engineering or Senior Director role don't hesitate to reach out to me via my [LinkedIn](https://linkedin.com/in/jimkrygowski).


## What it actually does

Ten skills, each a focused piece of the search, invoked in a normal Claude Code chat session:

| Skill | What it does |
|---|---|
| `bootstrap` | First-time setup — checks the Python preflight, then walks a new user through `build-profile` and `define-trajectory` |
| `build-profile` | Guided conversation to build a real candidate profile: career history, best/worst jobs and bosses, and the patterns underneath them |
| `define-trajectory` | Defines (and later revisits) the target role, shaped as a Mnookin Two-Pager — see below |
| `score-opportunity` | Scores a pasted job description against your actual must-haves/must-nots, criterion by criterion — not a vibe check |
| `tailor-resume` | Tailors a resume and cover letter from your master resume — never invents experience to fit a JD |
| `company-research` | Researches a target company, every finding tagged with a source |
| `interview-prep` | Briefing before a call — who you're talking to, likely questions, honest talking points including where you have a real gap |
| `interview-review` | Turns a call transcript into structured feedback and advances the pipeline |
| `career-coach` | A structured coaching session grounded in evidence-graded psychology frameworks — see below |
| `morning-scan` | A daily pipeline/email/calendar scan, run on demand — not a background job |

## Grounded in real frameworks

Two things this system leans on that most "AI job search assistant" projects don't bother with:

**The coaching is evidence-graded, not aspirational.** `career-coach` draws on seven frameworks — Schein's Career Anchors, Self-Determination Theory, Ibarra's Working Identity, Opportunity Fit Assessment, Career Capital, Regret Minimization, Ikigai — and every one of them ships with a companion [research review](.claude/skills/career-coach/research.md) that grades its actual evidence quality, cites the primary literature, and says plainly when a framework is a practitioner heuristic dressed up as science. Self-Determination Theory gets used with confidence — 40+ years of replicated peer-reviewed research. Ikigai gets used as a conversation starter and nothing more — it's a Western blog invention from 2011, misattributed to Japan ever since. The skill doesn't pretend otherwise, and neither does this README.

**The trajectory format comes from a real methodology.** `define-trajectory` builds a "Mnookin Two-Pager" — a concept from Phyl Terry's *Never Search Alone*, shaped as a genuine, shareable pitch document rather than internal notes. The system also implements Terry's Listening Tour idea directly: real feedback from an interview or a networking conversation is treated as a trigger to revisit the trajectory, not just a calendar-based staleness check. What's deliberately *not* here is Terry's Job Search Council — a peer accountability group is a real human structure, and no amount of agentic tooling should pretend to substitute for one.

## Built like software, not a prompt

A few things worth pointing at directly if you're evaluating engineering judgment rather than just features:

- **Engine and data are structurally separated.** Everything personal — your profile, your pipeline, your tracker — lives under `state/`, which is gitignored in its entirety. Pulling engine updates is a plain `git pull` that cannot touch or conflict with anyone's actual data, because that data was never tracked in this repo to begin with. That wasn't the first design — the initial build co-located data with the engine, separated only by naming convention, and got corrected once it became clear that didn't structurally hold. The commit history says so.
- **Agents are provided tools for common tasks.** For example, `tools/tracker.py` is the sole writer of the pipeline state, with a real file lock around every read-modify-write cycle — proven with a test that fires 8 concurrent writes at it and checks none get silently dropped. This exists because LLMs are by nature non-deterministic and rolling the dice each session by letting the LLM figure out how to edit the tracker is a recipe for corrupted files.
- **Guardrails are honest about what's structural versus what's a promise.** The agent is denied, at the tool-permission level, from ever calling the Gmail send/reply/forward tools — that one's enforced, not just instructed. The other guardrails (never invent experience, never assert an unsupported claim as fact) are instruction-level, and the system says so rather than overclaiming a guarantee it can't back up.
- **Real code review happened — by an adversarial agent, not the agent that wrote the code.** This system was built via spec → implementation plan → independent implementer/reviewer passes on every task, plus whole-branch reviews that caught real cross-task bugs (a stale onboarding path, a mislabeled data dependency) before merge. After the initial merge, an external review pass caught a genuine concurrency bug and a date-parsing bug that silently dropped messages — both fixed, both now covered by regression tests. Nothing here shipped on the first try and stayed that way.
- **Stdlib only.** `tools/tracker.py` and `tools/gmail_extract.py` have zero pip dependencies, including their test suites. No supply chain to audit for a tool that manages your job search pipeline.

## Layout

```
CLAUDE.md                        persona, guardrails, pointers to data files

state/                           gitignored — never part of this repo's git history
  career/
    profile.md                   your background (built by build-profile)
    trajectory.md                your target role, Mnookin Two-Pager shape
    job_alert_sources.md         your job alert email sources
    resume/master_resume.md      your source-of-truth resume
  opportunity/<Company>/<Role>/  per-opportunity JD, contacts, notes, tailored resume, transcripts
  tracker.md / tracker_closed.md active / closed pipeline state

tools/
  tracker.py                     sole writer of tracker.md, locked, tested
  gmail_extract.py                extracts new content from a saved Gmail thread

.claude/
  skills/                        the ten skills above
  commands/
    summarize-call.md            turns a call transcript into structured notes
```

## Getting started

```
git clone https://github.com/jimkrygowski/job-search-os.git
cd job-search-os
```

Then, in a Claude Code session in this directory, just say you want to get started — `CLAUDE.md` points a new user at the `bootstrap` skill automatically. It checks for Python 3, then walks you through building your profile and defining your target role. Everything after that — scoring opportunities, tailoring resumes, prepping for interviews, tracking the pipeline — happens through normal conversation.

## About me

Jim Krygowski — engineering executive, Boston MA. 25+ years building and scaling engineering organizations, most recently at the VP Engineering / Senior Director level, with a track record spanning large established orgs and growth-stage companies. Currently looking for the next CTO, VP Engineering, or Senior Director role where the problem is genuinely hard.

[linkedin.com/in/jimkrygowski](https://linkedin.com/in/jimkrygowski)
