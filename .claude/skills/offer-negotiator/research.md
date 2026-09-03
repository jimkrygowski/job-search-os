# Offer Negotiator Skill — Research Basis

This document records the evidence base for every tactic and comp-mechanics
claim the offer-negotiator skill relies on, what was evaluated, and why each
choice was made. It exists so the skill's advice is grounded in evidence,
not accumulated assumption — same purpose as `career-coach/research.md`.

Full bibliographic detail (journal, volume, pages, DOI) for every citation
lives in the companion file `research-source.md`, linked from each
subsection's Source line — kept separate so this file stays focused on
what actually drives the skill's advice.

**Research conducted:** September 1, 2026
**Scope:** Salary/offer negotiation tactics; equity and comp mechanics for a
U.S. tech job search.

---

## How to Use This Document

This file covers both negotiation tactics and equity/comp mechanics — no
single negotiation moment needs all of it. Read only the subsections a
given moment maps to below; skip the rest.

| Moment | Needs |
|---|---|
| Setup Mode | Anchoring & First Offers, BATNA (Best Alternative to a Negotiated Agreement) |
| 1. First-contact prep | Anchoring & First Offers, BATNA (Best Alternative to a Negotiated Agreement), Deflecting Salary History / Expectation Questions |
| 2. Offer breakdown | None directly — the Equity & Comp Mechanics reasoning is already baked into `tools/option_value.py`'s docstrings and called, not re-read here; market-benchmark sourcing follows CLAUDE.md guardrail #2, not this file |
| 3. Counter-negotiation planning | Integrative (Multi-Issue) Negotiation, Gender and Framing Effects in Salary Negotiation, Deadline and Pressure Tactics |
| 4. Final accept/decline hand-off | None — this moment hands off to `career-coach` without its own research session (design spec §6.4) |

---

## Negotiation Tactics

### Anchoring & First Offers

**Source:** Galinsky & Mussweiler (2001); extended by Loschelder et al.
(2014). [Full citation →](research-source.md#anchoring-first-offers)

**Evidence quality: High.** This is one of the most replicated findings in
negotiation research, running from Tversky & Kahneman's original anchoring
work through decades of negotiation-specific lab and field studies.

- Across three experiments, whichever party (buyer or seller) made the
  first offer ended up with a better final outcome, and first offers were
  a strong predictor of final settlement price — the classic
  "first-mover advantage."
- The mechanism is selective accessibility: negotiators receiving a first
  offer unconsciously search for reasons the anchor could be reasonable,
  which biases their counter-offer toward it.
- Loschelder et al. (2014) found that *precise* first offers (e.g. a
  number like $128,400 rather than a round $130,000) anchor more strongly
  than round ones of similar size — the recipient reads precision as a
  signal of real information/expertise and makes smaller counter-moves in
  response.
- Ames, D. & Mason, M.F. (2015). Tandem anchoring: Informational and
  politeness effects of range offers in social exchange. *Journal of
  Personality and Social Psychology*, 108(2), 254–274 — found that
  "bolstering" range offers (stating a target number, then stretching the
  range further in your favor, e.g. asking for "$15–20K above range"
  instead of a flat "$15K above range") can outperform a single point
  offer without the relational cost negotiators fear, because the range's
  low end signals reasonableness while the high end still anchors.

**Known limitations:**
- The first-mover advantage weakens or disappears when the other party has
  strong independent knowledge of the zone of possible agreement (ZOPA) —
  e.g., a recruiter who negotiates this role constantly and knows the
  band cold is much harder to anchor than one improvising.
- If the counterpart actively interrogates the rationale behind the first
  offer rather than just reacting to the number, the anchor's pull is
  reduced (per Galinsky & Mussweiler's own perspective-taking condition).
- Almost all underlying studies are lab/simulation-based (MBA students,
  paid participants in mock negotiations), not real salary negotiations
  with real career stakes — external validity to actual job offers is
  inferred, not directly tested at scale.

**How to use correctly:** When the user has good market data (a real
target range from `comp_target.md` or public comp data) and the employer
side is unlikely to have better information than they do, encourage them
to give a specific, well-justified number first rather than deflecting
indefinitely — waiting to be anchored by the employer's number gives away
the advantage. When the user doesn't yet know the role's real band, or the
counterpart (e.g. an in-house recruiter with full visibility into pay
bands) clearly has better information, deflecting to learn the employer's
number first is the better play. Precision and stated rationale (not round
numbers, not bare assertion) make a first offer land harder.

---

### BATNA (Best Alternative to a Negotiated Agreement)

**Source:** Fisher & Ury (1981), *Getting to Yes*; tested by Pinkley,
Neale & Bennett (1994) and extended by Pinkley (1995).
[Full citation →](research-source.md#batna)

**Evidence quality: Moderate-High.** BATNA itself is a conceptual/practitioner
framework, not an empirical finding — *Getting to Yes* is a practitioner
book built on the authors' mediation experience, not a research study. But
its central claim (a better alternative to a deal improves your outcome in
that deal) has been independently tested and replicated in experimental
negotiation research:

- Pinkley, Neale & Bennett (1994) manipulated BATNA strength (high, low, or
  none) in a controlled dyadic negotiation and found negotiators with a
  stronger BATNA achieved better individual outcomes — one of the more
  direct experimental confirmations of the concept.
- Multiple subsequent studies replicate the pattern that BATNA strength,
  and *knowledge* of the counterpart's BATNA specifically, predict
  individual and joint negotiation outcomes (e.g., White, Valley, Bazerman,
  Neale & Peck, 1994, and later work building on Galinsky & Mussweiler,
  2001, above). Pinkley's 1995 follow-up work (cited above) also found
  that the personal-gain advantage of holding a strong BATNA accrues
  mainly when *both* negotiators are aware of it — when only the
  BATNA-holder knows their own alternative and the counterpart doesn't,
  that personal-gain advantage weakens substantially, though joint gain
  and integrative trade-offs still rise when the BATNA-holder themself is
  aware of it. The leverage comes partly from the other side perceiving
  the alternative, not merely from possessing it.

**Known limitations:**
- The original *Getting to Yes* text is not itself a scientific study;
  treat "always know your BATNA" as well-supported practitioner wisdom
  with real (if narrower) experimental backing, not as a directly-tested
  claim on its own.
- Lab studies use artificial point-based negotiation exercises; a real
  job-offer BATNA (a competing offer, current job, savings runway) is
  harder to quantify cleanly than an experimental payoff matrix.
- A BATNA's power depends on the other side knowing or believing it exists
  — an un-communicated BATNA does little for leverage in most of this
  research.

**How to use correctly:** This is the concept `comp_target.md` (Bucket 3)
should be built around — before any negotiation session, the user's walk-
away point should be defined concretely (a competing offer, a real
timeline on their current job, or an honest number for "how long can I
search without an offer") rather than left as a vague sense of leverage.
The skill should push the user to articulate their actual BATNA, not an
aspirational one, and should note that a BATNA only creates leverage to
the extent the counterpart is made aware a credible alternative exists.

---

### Deflecting Salary History / Expectation Questions

**Source (legislative fact):** HR Dive salary-history-ban tracker (last
updated April 28, 2026). [Full citation →](research-source.md#deflecting-salary-history)

**Evidence quality for the legal claim: High (it's a tracker of enacted
law, not a research finding) — but time-sensitive.** As of the tracker's
April 2026 update: 22 U.S. states (including California, Colorado,
Connecticut, Illinois, Massachusetts, New York, Washington, and others)
plus Puerto Rico and roughly two dozen individual cities/counties
(San Francisco, Chicago, Philadelphia, and more) have laws barring
employers from *asking about or relying on* a candidate's salary history.
Most of these laws restrict only *asking*; some, like California's, also
bar using salary history even if an employer already has it or the
candidate volunteers it. Because state/local legislatures amend this
regularly, treat any specific list as a snapshot that should be re-verified
against a current tracker (e.g. HR Dive's) at time of use rather than
hard-coded — do not assume this list is exhaustive or current beyond the
tracker's stated update date.

**Critical distinction — salary *expectation* questions are different and
mostly still legal:** Salary history bans do not, in most jurisdictions,
prohibit an employer from asking what salary a candidate *expects* or
*wants* going forward. Some states' laws (e.g. Illinois, Nevada per the
same tracker) explicitly carve out and permit pay-expectation questions
even while banning history questions. This means "what's your expected
salary?" is a legal question almost everywhere in the U.S., and needs a
tactical answer, not a legal deflection — citing a salary history ban in
response to an expectation question is a category error.

**Evidence quality for the tactical response: Low — practitioner
consensus, not rigorous study.** No controlled study was found testing
which specific scripted response to a salary-expectation question (e.g.,
"what range has been budgeted for this role?" vs. stating a wide range
vs. stating a point figure) produces better outcomes in a real hiring
process. What sourcing exists is career-advice practitioner content
(Robert Half, Indeed, Coursera, and similar career-advice publishers), all
converging on similar advice — deflect to the employer's budgeted range
first if possible, delay committing to a number until role scope is
understood, and if a number must be given, ground it in market data. This
converges with, and is partially supported by, the more rigorous anchoring
and range-offer research above (Galinsky & Mussweiler 2001; Ames & Mason
2015) — whoever states a number first tends to anchor the outcome, so
deferring the number to the employer when you lack a confident target is
consistent with that literature, even though no study tests the salary-
interview-question scenario directly.

**Known limitations:**
- The legal landscape (which states ban what) is a fast-moving target;
  this file's specific state list should not be treated as permanently
  accurate.
- The tactical "how to answer" guidance is genuinely unsourced beyond
  practitioner convergence — flag this to the user as tactical opinion
  rather than as tested fact.

**How to use correctly:** State the legal fact plainly and note it's
current as of a specific date, with a pointer to re-check a live tracker
if precision matters (e.g. before an interview in a state not covered
above). Keep the tactical advice on expectation questions clearly labeled
as practitioner consensus grounded in adjacent anchoring research, not as
an independently validated finding.

---

### Integrative (Multi-Issue) Negotiation

**Source:** Walton & McKersie (1965); operationalized experimentally by
Pruitt & Lewis (1975) and colleagues through the 1970s–80s; popularized
for practitioners in Malhotra & Bazerman (2007), *Negotiation Genius*.
[Full citation →](research-source.md#integrative-negotiation)

**Evidence quality: Moderate-High for the underlying mechanism, Low-Moderate
for the popular practitioner packaging.** The core empirical finding —
that negotiators who trade across issues they weight differently
("log-rolling") achieve higher joint (and often individual) value than
negotiators who bargain issue-by-issue — comes from a real experimental
tradition (Pruitt and colleagues, 1970s–80s onward), not just from
*Negotiation Genius*, which is a practitioner synthesis book rather than a
primary research source.

- Log-rolling: when two parties have different priorities across issues
  (e.g. one cares more about base salary, the other's constraint is bonus
  budget), trading concessions across those issues produces outcomes
  better for both than issue-by-issue haggling. Traced to Froman, L.A. &
  Cohen, M.D. (1970). Compromise and logroll: Comparing the efficiency of
  two bargaining processes. *Behavioral Science*, 15(2), 180–183, and
  built on experimentally by Pruitt. A logrolling-procedure formalization
  for practical multi-issue negotiation training was published as Tajima,
  M. & Fraser, N.M. (2001). Logrolling Procedure for Multi-Issue
  Negotiation. *Group Decision and Negotiation*, 10(3), 217–235.
- Multiple Equivalent Simultaneous Offers (MESO): a technique for
  proposing several different packages of equal value to the offerer at
  once and letting the counterpart pick — this reveals counterpart
  priorities without a back-and-forth. Empirically tested by Leonardelli,
  G.J., Gu, J., McRuer, G., Medvec, V.H., & Galinsky, A.D. (2019).
  Multiple equivalent simultaneous offers (MESOs) reduce the negotiator
  dilemma: How a choice of first offers increases economic and relational
  outcomes. *Organizational Behavior and Human Decision Processes*, 152,
  64–83, across six experiments: MESOs produced stronger anchors, greater
  joint value, and left recipients more satisfied and more likely to view
  the offerer as cooperative than an equivalent single point offer.

**Known limitations:**
- Requires that the two sides actually have *different* priorities across
  issues (e.g., candidate values base pay more than signing bonus timing,
  employer has more flexibility on bonus than base). If priorities are
  identical, there is no integrative value to unlock and it reduces to
  pure distributive bargaining.
- Requires the negotiator to know (or credibly infer) their own priority
  ranking across issues *before* the conversation — the skill can't
  generate this for the user; it depends on `comp_target.md` (Bucket 3)
  correctly capturing which comp dimensions the user actually weights
  higher.
- Lab studies again dominate the evidence base; less field-validated in
  real one-off job-offer negotiations specifically (as opposed to
  recurring business/labor negotiations, which is where Walton & McKersie
  and Pruitt's tradition originates).

**How to use correctly:** This is the direct evidentiary basis for the
"package literacy" goal from the design's Purpose section — the skill
should coach the user to negotiate salary, sign-on bonus, equity, start
date, and other dimensions as a package with known relative priorities,
rather than sequentially anchoring on base salary alone and treating
everything else as fixed. Where the user hasn't stated a priority order
across comp dimensions, ask for one before suggesting trade language.

---

### Gender and Framing Effects in Salary Negotiation

**Source:** Babcock & Laschever (2003/2021), *Women Don't Ask*; Bowles,
Babcock & Lai (2007); contested/updated by Mazei et al. (2015)
meta-analysis and Kray, Kennedy & Lee (2024).
[Full citation →](research-source.md#gender-framing-effects)

**Evidence quality: Contested — treat with real caution.** This is
explicitly one of the more high-profile areas of negotiation research
where an influential early narrative has been complicated, and in places
undercut, by later and more rigorous work. Do not present "women don't
ask" as settled fact.

- Babcock & Laschever's original 2003 book argued women initiate
  negotiations roughly four times less often than men, and that this
  behavioral gap contributes meaningfully to the gender pay gap. This is a
  practitioner/trade book built on the authors' academic research program,
  not itself a single peer-reviewed study, though it draws on Babcock's
  academic work.
- Bowles, Babcock & Lai (2007) is a real, peer-reviewed experimental
  finding: evaluators penalized *female* candidates (but not male
  candidates) for initiating a compensation negotiation — a genuine
  "backlash effect" documented under controlled conditions.
- Mazei et al.'s 2015 meta-analysis (123 effect sizes, N=10,888) found
  gender differences favoring men in negotiation outcomes overall, but the
  gap shrank substantially — to the point of near-disappearing — when
  negotiators had negotiation experience, had explicit information about
  the bargaining range, or were negotiating on behalf of someone else
  rather than themselves. This is an important qualifier: the "gap" is not
  a fixed trait difference, it is heavily moderated by preparation and
  information, both of which a negotiation-prep skill can directly affect.
- Kray, Kennedy & Lee (2024, *Academy of Management Discoveries*, DOI
  10.5465/amd.2022.0021 — see research-source.md#gender-framing-effects
  for full citation) surveyed graduates of a top U.S. MBA program about
  whether they negotiated their first post-MBA salary, plus a second,
  larger survey of alumni about negotiating promotions/compensation more
  broadly. They found women now negotiate salary at rates equal to or
  exceeding men's — 54% of women vs. 44% of men negotiated salary in the
  first-job cohort, and 64% of women vs. 59% of men negotiated a promotion
  or compensation in the alumni cohort — directly complicating the
  original "women don't ask" framing two decades later. Secondary
  reporting on this paper gives slightly different sample sizes for the
  two survey waves — roughly 990–1,435 for the first-job cohort and
  roughly 1,939–2,000 for the alumni cohort, depending on the source —
  which could not be fully reconciled without the paper's own methods
  section. The percentage figures themselves are consistent across the
  journal's own abstract page, UC Berkeley Haas's research summary, and
  Harvard Law School's Program on Negotiation.
  Notably, the pay gap persisted in this same population despite equal or
  higher negotiation rates among women — but the paper's actual headline
  mechanism for that is **differential rejection, not structural
  factors**: the only gender difference the alumni survey found was that
  more women than men reported attempting to negotiate, *and* more women
  than men reported being turned down when they did. The paper's own
  framing is that a gender difference in negotiation propensity cannot
  account for the persisting pay gap in this population — the gap traces
  to how negotiation requests are received (women's asks being rejected
  more often), not to whether or how often women ask.
- Separately, research on negotiation "backlash" more broadly (the idea
  that assertive negotiating behavior is judged more harshly in women) is
  an area with documented replication concerns in the broader social
  psychology literature on gender and assertiveness; this skill did not
  locate a direct large-scale replication attempt specifically on the
  Bowles/Babcock/Lai 2007 paradigm, and treats that specific finding as
  credible but not re-confirmed at meta-analytic scale the way the general
  gender-negotiation-outcome gap has been (via Mazei et al. 2015).

**Known limitations:**
- The field has moved between three somewhat different claims over 20
  years: (1) women negotiate less than men, (2) the negotiation-outcome
  gap that does exist is heavily moderated by preparation/experience/
  information rather than a fixed trait, and (3) more recent survey
  evidence suggests the initiation-rate gap itself may have narrowed or
  reversed in at least some populations (MBA graduates) even as the pay
  gap persists for other reasons. A skill drawing on this research should
  not flatten it to "women don't ask" as a blanket claim.
- Much of the underlying experimental work uses student/lab samples;
  survey work like the 2024 study is self-report from a specific
  population (elite MBA graduates) and may not generalize broadly.
- Backlash effects, where documented, appear to interact with *how*
  someone negotiates (e.g., framing a request in relational/communal terms
  vs. purely self-interested terms) more than *whether* someone negotiates
  at all — this is a live area of ongoing research this document does not
  claim to have exhaustively covered.

**How to use correctly:** Do not tell a user "your gender predicts how you
should negotiate" as a general rule. What is well-supported enough to act
on: (1) preparation, market-rate information, and rehearsal reduce
whatever outcome gaps exist, regardless of the underlying cause — this is
squarely in the skill's control and directly actionable; (2) if a user
raises a concern about being judged for negotiating assertively, that
concern has real experimental grounding (Bowles, Babcock & Lai, 2007) and
should be taken seriously rather than dismissed, and framing requests with
a stated rationale (e.g., market-data-backed, not just "I want more") is
consistent with what that research and adjacent work on negotiation
framing suggests reduces backlash risk — but say so as reasonable
inference, not as a directly tested claim for the salary-negotiation
setting specifically.

---

### Deadline and Pressure Tactics

**Source:** Stuhlmacher, Gillespie & Champagne (1998) meta-analysis;
Moore (2004); on exploding offers specifically, Lau, Bart, Bearden &
Tsetlin (2014). [Full citation →](research-source.md#deadline-pressure-tactics)

**Evidence quality: Moderate-High for the general time-pressure effect;
Moderate for exploding-offer-specific outcomes — Lau et al. (2014) is
real behavioral-experimental evidence for a specific reciprocation
mechanism, though a field-measured retention/turnover statistic remains
unsourced.**

- Stuhlmacher et al.'s 1998 meta-analysis found time pressure reliably
  produces faster concessions, lower demands, and a higher likelihood of
  reaching agreement — the general mechanism is that urgency reduces
  negotiators' willingness (or perceived ability) to hold out. The effect
  was stronger for simpler negotiations and near deadlines, and weaker
  when the counterpart used a tough, inflexible strategy — meaning
  pressure tactics are somewhat self-defeating against a firm response.
  A related mechanism, reported in follow-up work — Stuhlmacher, A.F. &
  Champagne, M.V. (2000). The impact of time pressure and information on
  negotiation process and decisions. *Group Decision and Negotiation*,
  9(6), 471–491 — is that time
  pressure reduces systematic information processing (higher need for
  cognitive closure), which is consistent with why rushed decisions under
  a deadline tend to be worse ones.
- Moore (2004) found a genuinely counterintuitive result: revealing (not
  hiding) one's own final deadline can *improve* outcomes when time is
  costly to the discloser, because it lets the counterpart make efficient,
  final offers rather than dragging out low-ball moves — this cuts against
  the instinct to always hide a deadline, though it specifically concerns
  the discloser's own deadline, not one imposed on them by a counterpart.
- On "exploding offers" specifically (an offer with an artificially short
  fuse, e.g. "this expires in 24 hours"): Lau et al. (2014) is a
  **behavioral experimental** paper (not a formal/decision-theoretic
  model) — across multiple experiments, proposers chose between issuing
  an exploding offer or an extended one, and responders reacted under
  each condition. Proposers who issued exploding offers ended up
  substantially worse off, and that loss arises primarily from **negative
  reciprocation by responders after they accept an exploding offer**, not
  from responders making a rushed, low-information accept/reject decision
  in the moment. In other words,
  the harm to the offering party shows up *after* acceptance, through the
  responder retaliating (e.g., reduced cooperation) once they're in the
  relationship, not primarily through the responder picking badly at the
  moment of decision. Beyond Lau et al., most of what's written on
  exploding job offers specifically is practitioner/HR-trade commentary
  (e.g., that exploding offers correlate with poor early retention and
  candidate distrust). Lau et al.'s negative-reciprocation finding *is*
  direct experimental evidence for something adjacent to that
  distrust/retention claim — it demonstrates a real, causal mechanism by
  which an exploding offer damages the relationship after acceptance —
  but it does not measure employee turnover or retention as a field
  statistic. No rigorous field study quantifying actual post-hire
  turnover after an exploding offer was found; treat a specific "leads to
  X% higher turnover" claim as still unsourced
  practitioner consensus, distinct from the reciprocation/distrust
  mechanism itself, which now has real experimental backing via Lau et
  al. — do not conflate the two, and do not cite a specific turnover
  percentage without a verifiable source.

**Known limitations:**
- Almost all of this evidence, including Lau et al.'s exploding-offer
  experiments, comes from lab/simulation studies rather than field
  studies of real job-offer negotiations under real exploding deadlines —
  external validity to a candidate facing a real 48-hour offer deadline
  is inferred, not directly tested.
- The Moore (2004) finding about revealing one's own deadline is easy to
  over-extend; it does not say anything about how a candidate should react
  to a deadline unilaterally *imposed by the employer*, which is the more
  common real-world case this skill needs to address.

**How to use correctly:** This directly feeds counter-negotiation planning
(moment #3) — the skill should help the user recognize an artificially
short deadline as a pressure tactic with a well-documented general effect
(it does reliably produce faster, smaller-demand concessions across the
literature), and should coach a firm, calm response (e.g., politely asking
for a brief, specific extension and stating why) as consistent with the
finding that pressure tactics work less well against a firm counterpart.
Where relevant, it's fair to tell a user that exploding offers carry a
documented downside for the *employer* too (Lau et al.'s reciprocation
finding) — this is useful context for a user deciding how hard to push
back on one, but avoid stating a specific turnover-rate or retention
statistic tied to exploding offers, since no rigorously sourced field
figure was found for that specific claim.

---

## Equity & Comp Mechanics

<a id="exit-rate-base-rates"></a>
### Startup Exit-Rate Base Rates by Stage

**Source:** Correlation Ventures proprietary deal database, reported via
Booth (2013) and Levine (2014); cross-referenced against CB Insights'
startup post-mortem database and CB Insights' "The Venture Capital
Funnel" (2018); Mattermark/Rowley (2016); Carta (Peter Walker, three
posts, 2024 and 2026).
[Full citation →](research-source.md#exit-rate-base-rates)

**Evidence quality: Moderate for stage-to-stage graduation rates (real,
named, dated primary sources, cross-validated across independent
datasets); Low-Moderate for the aggregate all-stages figure (methodology
disagreements, dated, not stage-specific).** A 2026-09-02 research pass
(prompted by a user push-back that treating a Series A and a Series D
company identically was indefensible, and after independently rejecting
several fabricated or unattributed stage tables from other sources — see
"Rejected sources" below) found real per-stage graduation-rate data that
the original research pass missed.

- **CB Insights, "The Venture Capital Funnel"** (cbinsights.com/research/
  venture-capital-funnel-2/, published Sept 6, 2018; cohort of 1,119 US
  tech companies that raised seed funding 2008–2010, tracked through Aug
  31, 2018): 48% of companies graduated Seed→Series A (52% did not);
  63% of Series A companies graduated to Series B (37% did not);
  cumulative Seed→4th round (~Series C) was 15%. No percentage given past
  the 4th round — only "declining percentages at each subsequent stage,"
  with no number attached.
- **Mattermark/Rowley (2016)**, an independent dataset (2,011 US
  software companies that raised seed 2009–2012, using Mattermark/
  Crunchbase/AngelList data, tracking each company's terminal round
  raised): 31% graduated Seed→Series A (69% did not) — a real,
  independent data point, lower than CB Insights' 48%, consistent with
  this document's broader finding that outcomes vary substantially by
  cohort/vintage rather than contradicting it. Critically, this source
  states directly: *"the number of startups that raise a Series B halves
  and continues to halve in a stepwise function through Series F and
  beyond."* This is a real, named, dated, explicitly stated pattern — not
  a table this document is inferring.
- **Independent cross-validation of the "halving" pattern:** CB Insights'
  own numbers imply the same thing without any input from Mattermark.
  Cumulative Seed→B (derived: 0.48 × 0.63 ≈ 30.2%) versus CB Insights'
  own stated cumulative Seed→4th-round (15%) gives an implied Series
  B→C graduation rate of 15/30.2 ≈ 50% — matching Mattermark's stated
  halving pattern almost exactly, from an entirely different dataset,
  methodology, and research organization. Two independent sources
  converging on the same ~50% figure for the same transition is real
  evidence, not a coincidence this document is stretching.
- **Carta (Peter Walker, Head of Insights), "Series A to Series B Is the
  Hardest Startup Leap"** (Feb 25, 2026; cohort of 10,562 US startups
  that raised a Series A 2018–2025): graduation rate to Series B swings
  hard by vintage year — ~40% for 2020-vintage companies (2-year
  window), ~10–12% for 2022-vintage, ~20% for 2024-vintage improving.
  States "about half" of Series As graduate to B "in a strong cohort."
  This is a *shorter observation window* (1–2 years) than CB Insights'
  full-history tracking, so it likely overstates ultimate failure
  somewhat (some companies graduate later than the window captures) —
  but it's real, current (2026), and shows genuine downside risk in a
  weak macro environment that a single historical average would hide.
- **Carta (Peter Walker), "What Is a Good Seed to Series A Graduation
  Rate"** (Mar 18, 2026): benchmarks graduation-to-Series-A by time
  elapsed since seed — Year 1: 5%/10%/20% (low/med/high); Year 2:
  15%/25%/35%; Year 3: 20%/35%/45% — explicitly caveated that "the macro
  matters" as much as the stage itself.
- **Carta (Peter Walker), "The Startup Class of 2018 Where Are They
  Now"** (Mar 14, 2024; cohort of 3,067 US startups incorporated in
  2018, tracked ~6 years through 2024): gives a full furthest-stage-
  reached distribution, not just adjacent-round graduation — 38%
  pre-seed, 24% seed, 25% Series A, 10% Series B, 3.2% Series C, 0.7%
  Series D+ (plus outcomes: 45% ongoing, 49% shut down, 5% acquired,
  0.2% IPO'd). Converting this cascade into conditional stage-to-stage
  rates (cumulative-reached-≥X ÷ cumulative-reached-≥previous-stage)
  gives: Seed→A ~62% succeed (38% fail) — more optimistic than the
  range above; A→B ~36% succeed (64% fail) — within the range above;
  B→C ~28% succeed (**72% fail**); C→D+ ~18% succeed (**82% fail**).
  The B→C and C→D+ figures are notably more pessimistic than
  Mattermark's "halving" pattern (which implies ~50% at each of those
  transitions) — plausibly because this cohort's later rounds landed
  within the post-2022 funding correction.
- **Methodology decision, 2026-09-02, made explicitly by the user:**
  where sources disagree, this document uses the more pessimistic
  (higher-failure) figure, and prefers this newer Carta cohort (tracked
  through 2024) over Mattermark's older 2009–2012 cohort for the
  Series B/C/D+ transitions specifically, since more recent data is
  more likely to reflect the current fundraising climate. This is an
  explicit, owned choice to be conservative, not an attempt to average
  or split the difference — for the same reason, the Seed→A range
  below keeps its existing 52%–69% bounds rather than widening toward
  this cohort's more optimistic ~38% figure.
- **Rejected sources during this pass** (documented so this gap in the
  record doesn't get re-litigated): a synthetic 6-tier exit-rate/DLOM
  table from an external AI chat, with no real citations and numbers too
  uniform across 18 data points to be genuine; a second AI chat's
  "correction" that included a fabricated hybrid citation ("CB Insights
  Startup Genome / Cohort Study" — these are two real, unrelated
  organizations spliced together) and a misdated Correlation Ventures
  citation; a fractional-CFO marketing blog (zabella.net) whose
  stage-by-stage table had zero source attribution despite name-dropping
  real firms nearby; an internet-circulating "80% Series C failure rate"
  traced to a personal Medium blog styled as a journal, treated
  skeptically even by threads discussing it. None of these are used
  anywhere in this document.
- Booth's and Levine's original Correlation Ventures figures (all-stage
  aggregate, not stage-specific): 39% of deals went out of business
  (Booth), 65% of financings failed to return 1x capital (Levine), CB
  Insights' separate "3 out of 4" (75%) post-mortem figure. These three
  don't reconcile into one number (different methodologies, different
  windows) and remain useful only as a generic fallback for when a
  specific funding stage isn't known — see "How to use correctly."

**Known limitations:**
- **No source directly re-measures a Series D+→later transition** — the
  Series D+ default is held flat at the Series C→D rate as the most
  recent, most pessimistic available anchor, not an independently
  measured figure for that specific transition.
- **The Series B/C/D+ figures are derived arithmetic** (dividing one
  cohort's published cumulative-reach percentages), not a directly
  published conditional rate — the underlying published numbers (38%,
  24%, 25%, 10%, 3.2%, 0.7%) are real and cited exactly as Carta
  published them, but the division into stage-to-stage conditional
  rates is this document's own calculation, done transparently rather
  than left for `option_value.py` to reconstruct.
- **This document deliberately chose the more pessimistic, more recent
  figures over Mattermark's more optimistic, older ones for Series
  B/C/D+** — a real methodology disagreement exists between the two
  sources, and this is a conscious, owned choice to be conservative,
  not a claim that Mattermark's pattern was wrong.
- **Time-windowed vs. eventual-outcome methodologies don't mix
  cleanly.** CB Insights and Mattermark measure eventual/terminal
  outcomes (tracked for years); Carta's vintage-cohort figures are
  measured within a fixed 1–2 year window; the "Class of 2018" cascade
  is a 6-year snapshot, closer to eventual but still not fully
  terminal (45% of that cohort was still "ongoing," not resolved
  either way, as of the snapshot date). This document keeps these
  methodologies separate rather than blending them into one synthetic
  number.
- **None of these sources directly measure whether *common* stockholders
  received a payout** — "didn't graduate to the next round" is not the
  same claim as "common stock got zero." CB Insights states 67% of its
  full cohort ended up either dead *or* self-sustaining-but-non-venture-
  scale — a non-graduating company isn't necessarily a worthless one for
  common holders, and a graduating one isn't guaranteed to clear the
  preference stack either (see the next subsection). This document uses
  next-round graduation failure as a proxy for stage risk, not a direct
  measurement of common-stockholder outcomes.
- Booth's and Levine's aggregate Correlation Ventures figures remain
  dated (through 2013) and are secondary (partner blog posts, not the
  underlying dataset).

**How to use correctly:** For `option_value.py`'s exit-probability-
haircut defaults (spec §7, step 3), use a specific stage tier when the
user's company stage is known — real, sourced, per-stage figures now
exist:

| Stage tier | Failure rate | Source |
|---|---|---|
| Seed (→ Series A) | 52%–69% (range) | CB Insights (52%) to Mattermark (69%) — two independent cohorts. Deliberately not widened toward the more recent Carta cohort's more optimistic ~38% implied figure — see methodology decision above. |
| Series A (→ Series B) | 37%–85% (range) | CB Insights eventual outcome (37%) to Carta's worst observed vintage, short window (~85%). The 2018-cohort cascade implies ~64%, comfortably within this range. |
| Series B (→ Series C) | 72% | Derived from Carta's "Class of 2018" cascade (cumulative reach 3.9%/13.9%), chosen over Mattermark's older, more optimistic ~50% halving-pattern estimate per the recency/conservatism decision above. |
| Series C (→ Series D) | 82% | Same Carta cascade, same reasoning. |
| Series D+ (→ later) | 82% | No transition data exists past this cohort's Series D+ bucket; held flat at the Series C rate as the most recent, most pessimistic available anchor. |

When the specific stage isn't known, fall back to the generic all-stage
aggregate (roughly 60–75%, per Booth/Levine/CB Insights above) rather
than guessing a stage. **Caution — double-counting risk, regardless of
which tier is used:** several of the underlying figures (particularly
the generic aggregate) are downstream of fund-return data that already
partially reflects preference-stack subordination. Spec §7 applies the
exit-probability haircut (step 3) *in addition to* a separate
preference-stack haircut (step 2) — feeding a preferred-level or
company-disposition failure rate into the exit-probability step while
also subordinating common separately risks double-counting the same
effect. `option_value.py`'s design needs to account for this overlap
explicitly rather than stacking both haircuts naively.

---

<a id="liquidation-preferences"></a>
### Liquidation Preferences & the Preference Stack

**Source:** NVCA Model Legal Documents / Model Term Sheet; Cooley LLP
*Venture Financing Report* (Q1 2026 edition); The Holloway Guide to
Venture Capital, "Liquidation Preference" (edition 1.1.4).
[Full citation →](research-source.md#liquidation-preferences)

**Evidence quality: High for the mechanism and for current market-standard
single-round terms; unverified for cross-round stacking base rates.**

- **The mechanism** is uncontested, well-documented corporate-finance/
  venture-law mechanics, codified in the NVCA's standard model documents
  used across the industry: a liquidation preference is a contractual
  right for preferred stockholders to be paid a specified amount before
  any proceeds go to common stockholders in a liquidity event. Under a
  **1x non-participating** structure (the current market standard — see
  below), preferred holders receive the *greater of* their liquidation
  preference or their as-converted pro-rata common share — a choice
  between the two, not both. Under a **participating** structure,
  preferred holders receive their preference *and then also* share
  pro-rata in the remaining proceeds alongside common ("double-dipping"),
  which can severely reduce what's left for common and option holders in
  a moderate-value exit.
- **Stacking across rounds:** each financing round typically creates its
  own class of preferred stock with its own liquidation preference. Per
  the Holloway Guide, the order in which these classes get paid (the
  "preference stack") is set contractually and varies by deal — it can be
  *pari passu* (all preferred classes rank equally and split available
  proceeds pro rata if insufficient to pay everyone in full) or a
  strict seniority order, sometimes structured "last money in, first
  out" (the most recent round's investors are paid before earlier
  rounds'). The practical effect for common and option holders is that
  the relevant floor below which they get nothing is the **sum of all
  outstanding preferences across every round**, not just the most recent
  round — a company that raised $150M in total preferred capital across
  five rounds needs an exit well above that combined figure before common
  sees meaningful value, even if every individual round used
  founder-friendly 1x non-participating terms.
- **Current market-standard terms (single round):** Cooley's Q1 2026
  Venture Financing Report found 98.2% of deals had a 1x liquidation
  preference and 96.4% used nonparticipating preferred stock; prior
  2025 quarters in the same series showed comparable figures (95–98%
  for 1x, 96–97% for nonparticipating). This confirms that participating
  preferred and above-1x multiples are currently rare in individual
  rounds, at least among the deals Cooley's practice sees.

**Known limitations:**
- Cooley's data reflects deals worked by one (large, prominent) law firm's
  own venture practice, which skews toward well-lawyered, VC-heavy-market
  deals — it is not a random sample of all financings, and smaller or
  less-institutional rounds may look different.
- "Individual rounds are founder-friendly" does not imply the aggregate
  preference stack is small — stacking is precisely the mechanism by which
  several individually reasonable-looking rounds combine into a large
  cumulative floor. This document did not find a credible, cited base
  rate for "typical aggregate preference stack as a percentage of a
  company's most recent valuation" — that figure is company-specific and
  should be treated as unknown rather than estimated from a generic
  constant.
- Whether stacking is pari passu or strict-seniority is deal-specific;
  no source found here gives an industry-wide base rate for how often
  each structure is used.
- A Carta figure surfaced in search results (~70% of Series A financings
  use 1x non-participating preferred, as of 2023) could not be
  independently verified — Carta's site returned an access error to
  direct fetching — so it is not cited as a primary claim above, only
  noted here as an unverified secondary data point. It is notably lower
  than Cooley's figure (96.4%/98.2%, above) — an unresolved ~26–28
  percentage-point gap, possibly due to different denominators (Series A
  only vs. all rounds) or different report vintages.

**How to use correctly:** For `option_value.py`'s preference-stack haircut
default (spec §7, step 2), the mechanically correct input is the
**total contractual liquidation preference outstanding across all
preferred rounds for the specific company**, not a generic "typical %"
haircut inferred from market surveys — this is company-specific
information (from a cap table or data room) that a generic constant
cannot substitute for. If the tool needs a fallback when that data isn't
available, it should be treated as an explicit placeholder requiring user
confirmation, not a silently-applied default, since no authoritative
source here gives a credible "typical aggregate stack as % of valuation"
figure to hardcode. The 1x-non-participating market-standard finding above
is useful context for explaining terms to a user, but it describes single
rounds, not the cumulative stack that actually determines the common
stockholder's outcome.

**Conflict with the design spec (needs resolution in Bucket 2):** the
preference-stack haircut should be an explicit placeholder requiring user
confirmation, not a silently-applied default — which conflicts with spec
§7 step 2's call for the haircut to be "applied as a disclosed default,
overridable if the user knows the actual preference terms." That tension
needs to be resolved explicitly when Bucket 2 (`option_value.py`) is
designed: no source found here supports a credible generic "typical
stack as % of valuation" number to serve as that default, so step 2's
design either needs a different fallback (e.g. requiring the user to
supply the figure before proceeding) or an explicit, clearly-labeled
placeholder value that is not presented to the user as a real disclosed
default.

---

### 409A Valuation vs. Preferred Price Gap

**Source:** Moon (2020), Andreessen Horowitz (a16z); AICPA Practice Aid
(2013 revision, the last full revision as of September 2026); Internal
Revenue Code §409A. [Full citation →](research-source.md#409a-valuation-gap)

**Evidence quality: Moderate-High for the mechanism; Low for any specific
numeric ratio — and the best source found here explicitly warns against
citing one.**

- **Why the gap exists (mechanism):** a 409A valuation determines the
  fair market value of *common* stock specifically, for use as an ISO/NSO
  strike price. Under the option-pricing method described in the AICPA
  Practice Aid, common stock is modeled as a call option on the company's
  total equity value, struck at the point where the outstanding
  liquidation preference stack (see previous subsection) is exhausted —
  because common is legally subordinate to preferred and shares in
  liquidity risk. A 409A valuation that is lower than what sophisticated
  investors just paid for preferred stock in the same round is therefore
  not an accounting trick or an arbitrary "discount" — it is the
  mathematically expected result of common's contractual subordination
  (no liquidation preference, no anti-dilution or other protective
  rights) plus its illiquidity, correctly modeled.
- **How much lower in practice — the honest gap:** Moon's a16z article
  explicitly and directly debunks the commonly repeated rule of thumb that
  common FMV runs "10–20% of the most recent preferred round," stating
  "only in rare instances is a privately-held company's common stock FMV
  legitimately 10–20% of the value [of preferred]," and that there is no
  reliable universal ratio — the real number depends on each company's
  specific capital structure (size of the preference stack relative to
  current value), stage/proximity to a likely exit, and volatility.
  Several vendor/marketing sites publish specific stage-by-stage ratio
  tables (e.g., claiming ~10–30% at seed narrowing to ~45–70% at late
  stage) but this research could not verify those figures against any
  primary or rigorously sourced practitioner document, and the credible
  source found (a16z) explicitly warns against exactly this kind of
  simplified lookup table. Those vendor figures are deliberately **not**
  cited above as findings — they read as unsupported marketing content
  dressed up as a benchmark.

**Known limitations:**
- No credible, verifiable numeric ratio or range was found for "how much
  lower, on average, is 409A vs. preferred price." The best available
  source (a16z) argues that any single ratio is misleading.
- 409A valuations are refreshed periodically (typically ~annually or
  after a material event, not continuously), so the observed "gap" at any
  moment reflects a valuation that may already be stale relative to the
  company's current trajectory.
- The AICPA Practice Aid is a technical methodology reference, not itself
  a source of empirical "typical ratio" statistics.

**How to use correctly:** Explain the mechanism clearly and accurately —
strike price is deliberately lower than what preferred investors paid,
and that's the correct result of common's subordination, not a red flag
by itself. For `option_value.py`, do **not** hardcode a "typical ratio by
stage" default — that is precisely the kind of unsupported constant no
credible source substantiates, and the one credible source found warns
explicitly against it. If a numeric estimate is genuinely needed,
prefer deriving it from the same residual-claim mechanics already used
for the preference-stack and DLOM subsections (i.e., compute common's
value as a residual after the preference stack, then apply an illiquidity
discount) rather than looking up a stage-based ratio table.

---

<a id="dlom"></a>
### Discount for Lack of Marketability (DLOM)

**Source:** Damodaran (2005) synthesis of eight primary marketability-
discount studies (Maher 1976; Silber 1991; Johnson 1999; Wruck 1989;
Hertzel & Smith 1993; Bajaj et al. 2001; Emory 1996; Longstaff 1995).
[Full citation →](research-source.md#dlom)

**Evidence quality: High for the existence and rough order of magnitude of
an illiquidity discount as a real, mainstream finance concept; Moderate at
best for any single point estimate — the studies genuinely disagree by a
wide margin depending on methodology, and Damodaran's own synthesis is
explicitly skeptical of the highest figures.**

- **Restricted stock studies** (SEC Rule 144 private placements by
  already-public companies, compared to the same company's freely
  tradable stock at the same time): Maher (1976, 4 mutual funds,
  1969–73) found an average discount of 35.43%. Silber (1991,
  1981–88) found a median discount of 33.75%, larger for smaller/less
  healthy firms and larger blocks. Other studies broadly converge on
  30–35%; Johnson (1999) found a smaller ~20% discount. Damodaran flags
  these as based on small samples spread over long periods with
  substantial standard errors, and subject to selection bias — firms
  that make restricted placements tend to be smaller and riskier than
  the typical firm, and the buyers of restricted stock may be providing
  other services to the company for which the discount is partial
  compensation, not pure payment for illiquidity.
- **Controlled comparisons isolating the pure marketability effect**
  (restricted vs. registered private placements, to net out
  confounds like firm risk and buyer services): Wruck (1989) found only
  a 17.6% average / 10.4% median difference between restricted and
  registered placements. Hertzel & Smith (1993, 106 placements,
  1980–87) found a 13.26% median discount across all private placements,
  with restricted stock discounted 13.5 percentage points more than
  registered stock. Bajaj et al. (2001, 88 placements, 1990–97) found
  median discounts of 9.85% (registered) vs. 28.13% (restricted), but
  after controlling for differences across the issuing firms, attributed
  only **7.23%** specifically to marketability — a materially smaller
  number than the raw restricted-stock studies imply, once selection
  bias is controlled for.
- **Pre-IPO transaction studies** (private trades in the months/years
  before a company's IPO, compared to the IPO price): Emory (1996) found
  an average ~45% discount for trades in the 5 months pre-IPO. Willamette
  Associates extended this to trades up to 3 years pre-IPO (adjusted for
  P/E changes) and found discounts ranging 32–75%. Damodaran is
  explicitly skeptical of these: "It is difficult to see why an investor
  would be willing to accept a 40% discount on estimated value if an
  initial public offering is forthcoming. It seems likely that what these
  studies conclude is a marketability discount is reflective of other
  factors" (e.g., information asymmetry, control, selection).
- **Option-pricing / theoretical upper bound** (Longstaff 1995,
  formalized in Damodaran's Figure 3): models the value of marketability
  as a look-back option held by a perfect market timer, giving explicit
  **upper bounds** that scale with both the trading-restriction period
  and volatility. At 20% annualized volatility: ≈17% for a 1-year
  restriction, ≈25% for 2 years, ≈41% for 5 years. At 30% volatility:
  ≈26% (1 year), ≈39% (2 years), ≈66% (5 years). Damodaran stresses these
  are explicit *upper bounds* under an unrealistic perfect-timing
  assumption — actual discounts should be lower.

**Known limitations:**
- No source found here studies privately-held venture-backed startup
  common stock specifically — the underlying studies are drawn from
  already-public-company restricted stock, private placements, and
  pre-IPO trades. Startup 409A practice draws on this same body of
  literature (via the AICPA Practice Aid, see previous subsection) by
  analogy rather than through startup-specific empirical studies.
- The size of the discount is explicitly and heavily dependent on
  assumed holding period and volatility (per the option-pricing
  approach) — there is no single defensible constant independent of
  those inputs.
- The underlying primary studies are old (1970s–1990s); this synthesis
  paper itself dates to 2005. No comparably rigorous, more recent
  re-study of restricted-stock or pre-IPO discounts was found.
- The estimates vary enormously by methodology — from 7.23% (Bajaj et
  al.'s controlled estimate) to 66%+ (Longstaff's upper bound at high
  volatility and a long horizon) — so citing any single number without
  its methodology is misleading.

**How to use correctly:** For `option_value.py`'s time-value/illiquidity
discount default (spec §7, step 4), be honest that the literature does
**not** converge on a point estimate. The underlying studies span a
genuinely wide, unresolved range — roughly **7% (Bajaj et al.'s
*controlled* marketability-only estimate, after removing selection bias
and other confounds) up to 40%+** (pre-IPO transaction studies and
Longstaff's option-pricing bounds at longer horizons/higher volatility),
depending heavily on methodology, holding-period assumption, and
volatility. A default in roughly the **20–30%** region is a defensible
**judgment call that sits within that range**, not a figure where
multiple independent studies converge on the same number. In particular,
do not justify 20–30% by citing "Bajaj et al.'s 7–28% range depending on
control" as if both ends were still live support — the 28.13% figure is
Bajaj et al.'s *raw, uncontrolled* discount, and the subsection above
already explains why that number is the less credible one (it doesn't
isolate marketability from firm-selection effects); their actual
controlled estimate is 7.23%. Reintroducing the higher, uncontrolled
number here would contradict what this document already established
about it. Longstaff's option-pricing figures (roughly 17%–66%+ depending
on horizon and volatility) are explicit **upper bounds** under an
unrealistic perfect-timing assumption, not typical-case estimates —
actual discounts should be lower than those bounds, consistent with what
the subsection above already says. One factor that cuts *against*
understating the discount, however: several of the underlying studies
anchor to 1–2 year holding-period horizons (e.g. the moderate-volatility
option-pricing estimates cited above), while a typical startup's actual
time-to-liquidity — time from a given equity grant to an eventual IPO or
acquisition — often runs considerably longer than that in practice. A
longer real-world horizon pushes the option-pricing-derived bound higher,
not lower, so a 20–30% default should not be treated as conservative on
that basis alone; if anything it may understate the illiquidity discount
for a company with a long expected time-to-liquidity. Where possible, the
tool should let time horizon and volatility inputs move the estimate
(consistent with the option-pricing approach) rather than silently
applying one flat constant regardless of the user's actual situation.

---

### ISO vs. NSO Tax Treatment and AMT (flagged, not modeled)

**Source:** National Center for Employee Ownership (NCEO); Internal
Revenue Code §422, §56(b)(3), §83.
[Full citation →](research-source.md#iso-nso-tax-treatment)

**Evidence quality: High.** This subsection describes settled, uncontested
U.S. federal tax mechanism (Internal Revenue Code provisions), not a
contested empirical research finding — the "evidence quality" question
here is about whether the mechanism is accurately described, not about
weighing conflicting studies. NCEO is a long-established nonprofit
research/education organization focused specifically on employee
ownership and equity compensation, and its description of the mechanism
matches the underlying statutory sections.

**The mechanism (explanatory only — no personal tax computation):**

- **NSOs (nonqualified/nonstatutory stock options):** at exercise, the
  spread between fair market value and the exercise (strike) price is,
  under IRC §83, immediately treated as ordinary compensation income —
  subject to income and payroll tax withholding, reported on the
  employee's W-2 the same as a cash bonus. At a later sale, only further
  appreciation since exercise is treated as a capital gain (short- or
  long-term depending on the holding period measured from the exercise
  date). This is a single, immediate, and certain tax event at exercise.
- **ISOs (incentive stock options):** if granted under a qualifying plan
  and specific IRC §422 holding-period requirements are met — shares held
  at least two years from the grant date *and* at least one year from the
  exercise date before sale (a "qualifying disposition") — the employee
  owes **no regular income tax at exercise at all**, and the entire gain
  from strike price to eventual sale price is taxed as a long-term
  capital gain only when sold. However, the exercise-time spread (FMV at
  exercise minus strike price) is not simply tax-free — under IRC
  §56(b)(3) it becomes an Alternative Minimum Tax "preference item,"
  added back into a separate, parallel tax calculation the taxpayer must
  also run for that tax year. If the resulting AMT liability exceeds
  regular tax liability, the taxpayer owes the higher AMT amount instead
  of (in addition to, in effect) their regular tax.
- **Why this creates real risk:** because the AMT preference item is
  based on the *spread at exercise* — a paper gain — a person can exercise
  ISOs in a private, illiquid company, owe real cash AMT that same tax
  year on stock they cannot sell (there is no market for private-company
  common stock to raise the cash), and if the company's value later falls
  before any liquidity event, they may have paid real tax on a gain that
  no longer exists by the time they could actually realize it. (NCEO
  notes that excess AMT paid generally becomes a "minimum tax credit"
  that can offset regular tax liability in future years — a partial, not
  full or immediate, mitigant.)
- **Disqualifying dispositions:** if ISO shares are sold before the
  two-year/one-year holding requirements are met, the position reverts
  largely to NSO-like ordinary-income treatment on some or all of the
  spread instead of the preferential capital-gains treatment.
- **The core one-line contrast:** NSOs create a smaller, certain,
  immediate tax bill at exercise; ISOs can create zero regular tax at
  exercise but expose the holder to AMT risk precisely because the gain
  being taxed is on stock that, for a private company, cannot yet be sold
  to cover that tax.

**Known limitations:**
- AMT exemption amounts, phase-out thresholds, and rates are set by
  statute and adjusted (sometimes by legislation, sometimes by inflation
  indexing) essentially every year — none are cited here as durable
  facts, and none should be hardcoded anywhere in this skill.
- The actual AMT impact for any individual depends on their full tax
  picture (other income, filing status, state of residence, other AMT
  preference items) — this is inherently a personal calculation, not a
  general fact this document can responsibly state.
- State tax treatment of ISOs and AMT varies by state (e.g., California
  has its own, separately calculated AMT regime) and is out of scope
  here entirely.

**How to use correctly: this subsection is explanatory only.** Per the
design spec (§2/§7), `option_value.py` must not compute a user's AMT
liability, estimated tax owed, or any other personalized tax outcome —
v1 of this skill is pre-tax only. The correct use of this research is to
give the skill accurate language to explain *why* an ISO exercise
decision carries AMT risk and how that risk mechanically differs from an
NSO exercise, so it can flag the issue and prompt the user to model their
specific numbers with a qualified tax advisor or CPA — not to estimate or
recommend a number itself. Do not let this subsection's content expand,
in the skill's actual runtime behavior, into per-user tax estimation or
recommendation of any kind.

