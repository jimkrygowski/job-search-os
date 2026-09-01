# Offer Negotiator Skill — Research Basis

This document records the evidence base for every tactic and comp-mechanics
claim the offer-negotiator skill relies on, what was evaluated, and why each
choice was made. It exists so the skill's advice is grounded in evidence,
not accumulated assumption — same purpose as `career-coach/research.md`.

**Research conducted:** September 1, 2026
**Scope:** Salary/offer negotiation tactics; equity and comp mechanics for a
U.S. tech job search.

---

## Negotiation Tactics

### Anchoring & First Offers

**Source:** Galinsky, A.D. & Mussweiler, T. (2001). First offers as anchors:
The role of perspective-taking and negotiator focus. *Journal of Personality
and Social Psychology*, 81(4), 657–669. Extended by Loschelder, D.D.,
Stuppi, J., & Trötschel, R. (2014). "€14,875?!": Precision boosts the
anchoring potency of first offers. *Social Psychological and Personality
Science*, 5(4), 491–499.

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

**Known limitations / boundary conditions:**
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

**Source:** Fisher, R. & Ury, W. (1981). *Getting to Yes: Negotiating
Agreement Without Giving In*. Houghton Mifflin (3rd ed. with Bruce Patton,
Penguin, 2011). Originated at the Harvard Negotiation Project. Empirically
tested by Pinkley, R.L., Neale, M.A., & Bennett, R.J. (1994). The
impact of alternatives to settlement in dyadic negotiation. *Organizational
Behavior and Human Decision Processes*, 57(1), 97–116.

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
  2001, above). Pinkley's follow-up work also found that when negotiators
  know only their *own* BATNA and not the counterpart's, the outcome
  advantage from a strong BATNA weakens — the leverage comes partly from
  the other side perceiving it, not merely from possessing it.

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

**Source (legislative fact):** HR Dive, *Salary history bans: A running
list of states and localities* (tracker, last updated April 28, 2026).
Cross-referenced against state government sources cited in the tracker.

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

**Source:** Walton, R.E. & McKersie, R.B. (1965). *A Behavioral Theory of
Labor Negotiations*. McGraw-Hill — originated the distributive/integrative
distinction. Operationalized experimentally by Pruitt, D.G. (multiple
studies from the 1980s, e.g. Pruitt, D.G. & Lewis, S.A., 1975, Development
of integrative solutions in bilateral negotiation, *Journal of Personality
and Social Psychology*, 31(4), 621–633) using a three-issue negotiation
task with Peter Carnevale. Popularized for practitioners in Malhotra, D. &
Bazerman, M.H. (2007). *Negotiation Genius*. Bantam.

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
  built on experimentally by Pruitt.
  Thompson, L. (2003) also
  reports a logrolling-procedure formalization for practical multi-issue
  negotiation training (*Group Decision and Negotiation*).
- Multiple Equivalent Simultaneous Offers (MESO): a technique (associated
  with Leigh Thompson's negotiation research program, e.g. Thompson, L. &
  Leonardelli, G., 2004 discussions of the negotiator's dilemma) where a
  negotiator proposes several different packages of equal value to
  themselves at once and lets the counterpart pick — this reveals
  counterpart priorities without a back-and-forth, and research finds
  MESO offers are more likely to be accepted and leave counterparts more
  satisfied with the deal than an equivalent single point offer.

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

**Source:** Babcock, L. & Laschever, S. (2003, updated ed. 2021). *Women
Don't Ask: Negotiation and the Gender Divide*. Princeton University Press.
Bowles, H.R., Babcock, L., & Lai, L. (2007). Social incentives for gender
differences in the propensity to initiate negotiations: Sometimes it does
hurt to ask. *Organizational Behavior and Human Decision Processes*,
103(1), 84–103. Contested/updated by: Mazei, J., Hüffmeier, J., Freund,
P.A., et al. (2015). A meta-analysis on gender differences in negotiation
outcomes and their moderators. *Psychological Bulletin*, 141(1), 85–104.
And: Kray, L., Kennedy, J.A., & Lee, M. (2024) survey-based study
reported via Harvard's Program on Negotiation, on MBA graduates' current
negotiation initiation rates.

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
- A 2024 survey-based study (Kray, Kennedy & Lee, reported via Harvard's
  PON, original publication in *Academy of Management Discoveries*) of
  nearly 1,000 MBA graduates found women now negotiate salary and
  promotions at rates equal to or exceeding men's (e.g., 54% of women vs.
  44% of men negotiated salary in one cohort surveyed) — directly
  complicating the original "women don't ask" framing two decades later.
  Notably, the pay gap persisted in this same sample despite equal or
  higher negotiation rates among women, which the researchers attribute to
  structural factors (career trajectory, promotion access) rather than
  individual negotiation behavior.
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

**Source:** Stuhlmacher, A.F., Gillespie, T.L., & Champagne, M.V. (1998).
The impact of time pressure in negotiation: A meta-analysis. *International
Journal of Conflict Management*, 9(2), 97–116. Moore, D.A. (2004). Myopic
prediction, self-destructive secrecy, and the unexpected benefits of
revealing final deadlines in negotiation. *Organizational Behavior and
Human Decision Processes*, 94(2), 125–139. On exploding offers
specifically: Lau, N., Bart, Y., Bearden, J.N., & Tsetlin, I. (2014).
Exploding offers can blow up in more than one way. *Decision Analysis*,
11(3), 171–188.

**Evidence quality: Moderate-High for the general time-pressure effect;
Lower/mixed for exploding-offer-specific outcomes.**

- Stuhlmacher et al.'s 1998 meta-analysis found time pressure reliably
  produces faster concessions, lower demands, and a higher likelihood of
  reaching agreement — the general mechanism is that urgency reduces
  negotiators' willingness (or perceived ability) to hold out. The effect
  was stronger for simpler negotiations and near deadlines, and weaker
  when the counterpart used a tough, inflexible strategy — meaning
  pressure tactics are somewhat self-defeating against a firm response.
  A related mechanism, reported in follow-up work (Stuhlmacher & Champagne,
  2000, *Group Decision and Negotiation*, 9(6), 471–491), is that time
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
  quantitative decision-analysis paper modeling how exploding offers can
  backfire on the *offering* party by inducing premature, low-information
  acceptance/rejection decisions that don't serve either side well; this
  is decision-theoretic modeling, not a field study of real recruiting
  outcomes. Beyond this, most of what's written on exploding job offers
  specifically is practitioner/HR-trade commentary (e.g., that exploding
  offers correlate with poor early retention and candidate distrust) — no
  rigorous field study quantifying employee turnover after an exploding
  offer was found in this research pass; treat that specific "leads to
  turnover" claim as plausible practitioner consensus, not as an
  established statistic, and do not cite a specific turnover percentage
  without a verifiable source.

**Known limitations:**
- Almost all of this evidence comes from lab/simulation studies (or, for
  Lau et al., a formal model) rather than field studies of real job-offer
  negotiations under real exploding deadlines — external validity to a
  candidate facing a real 48-hour offer deadline is inferred, not directly
  tested.
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
Avoid stating a specific turnover-rate or retention statistic tied to
exploding offers, since no rigorously sourced figure was found for that
specific claim.

