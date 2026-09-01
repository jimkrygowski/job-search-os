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
And: Kray, L.J., Kennedy, J.A., & Lee, M. (2024). Now, Women Do Ask: A
Call to Update Beliefs about the Gender Pay Gap. *Academy of Management
Discoveries*, 10(1), 7–33. DOI: 10.5465/amd.2022.0021. (Published online
August 15, 2023; formal issue year 2024.) Re-verified directly against
the journal's own page (journals.aom.org) and UC Berkeley Haas's research
summary (haas.berkeley.edu/ibsi) for this fix — not just secondary
reporting.

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
- Kray, Kennedy & Lee (2024, *Academy of Management Discoveries* —
  full citation above) surveyed graduates of a top U.S. MBA program about
  whether they negotiated their first post-MBA salary, plus a second,
  larger survey of alumni about negotiating promotions/compensation more
  broadly. They found women now negotiate salary at rates equal to or
  exceeding men's — 54% of women vs. 44% of men negotiated salary in the
  first-job cohort, and 64% of women vs. 59% of men negotiated a promotion
  or compensation in the alumni cohort — directly complicating the
  original "women don't ask" framing two decades later. (Secondary
  reporting on this paper gives slightly different sample sizes for the
  two survey waves — e.g. roughly 990–1,435 for the first-job cohort and
  roughly 1,939–2,000 for the alumni cohort, depending on the source —
  which this document was not able to fully reconcile without reading the
  paper's own methods section; the percentages themselves were consistent
  across every source checked.) Notably, the pay gap persisted in this
  same population despite equal or higher negotiation rates among women,
  which the researchers attribute to structural factors (career
  trajectory, promotion access) rather than individual negotiation
  behavior.
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

---

## Equity & Comp Mechanics

### Startup Exit-Rate Base Rates by Stage

**Source:** Correlation Ventures proprietary deal database, reported via
two independent intermediary sources presenting different cuts of what
appears to be overlapping data: Bruce Booth (partner, Atlas Venture),
"Correlation's Fresh Look At Venture Capital Returns," *LifeSciVC*,
November 18, 2013 (analysis of 7,976 realized VC financings, 2003–2012,
exit-year basis); and Seth Levine (partner, Foundry Group), "Venture
Outcomes are Even More Skewed Than You Think," *VC Adventure*, August
2014 (analysis of 21,640 financings, 2004–2013, financing-level return
multiples). Also: Hassan, K., Varadan, M., & Zeisberger, C. (2020).
[Institutional Investor op-ed] citing a related Correlation Ventures
figure (0.4% of deals return 50x+). Cross-referenced against CB Insights,
*Why Startups Fail* research / startup post-mortem database (483
post-mortems tracked; 2024 update analyzed 431 VC-backed companies that
shut down since 2023), cbinsights.com.

**Evidence quality: Low-Moderate, and this is the weakest-sourced
subsection in this document — read the limitations below before treating
any number here as a default.** These are the best publicly available
proxies found, not a direct answer to the question asked.

- Booth's write-up of the Correlation Ventures dataset (7,976 financings,
  2003–2012): 39% of deals went out of business (zero return), 29% exited
  for less than invested capital, 32% returned a positive multiple (>1x).
- Levine's write-up of a different cut of Correlation Ventures data
  (21,640 financings, 2004–2013, at the individual-financing level rather
  than the company level): 65% of financings failed to return 1x capital,
  only 10% returned 5x or more, only 4% returned 10x or more.
- CB Insights' post-mortem tracking: roughly "3 out of 4" (75%) of
  venture-backed startups fail — a company-shutdown statistic drawn from
  CB Insights' own curated database of startups whose failure became
  public and documented, not an audited census of all VC-backed
  companies.
- These figures are not reconcilable into one clean number: the 39%/65%/
  75% figures each measure something different (company disposition vs.
  financing-level return multiple vs. self-selected shutdown tracking)
  over different, overlapping windows, using an undisclosed, proprietary
  methodology (Correlation Ventures is a VC firm, not an independent
  academic or regulatory data source, and its full dataset/methodology
  has not been independently peer-reviewed).

**Known limitations:**
- **None of these sources break results out by financing stage**
  (early-stage private vs. late-stage private vs. public) in the way this
  subsection was asked to research. No credible source doing that specific
  stage-by-stage breakdown was found in this research pass — several
  vendor/blog aggregator pages (not cited here) present stage-by-stage
  "probability of exit" tables, but their methodology and underlying data
  source could not be verified as credible, so they are omitted rather
  than cited.
- **None of these sources directly measure whether *common* stockholders
  received a payout**, which is the thing that actually matters for an
  option-value estimate. "Company went out of business" (Correlation's
  39%, CB Insights' 75%) is a reasonable proxy for a zero-payout outcome,
  but a company can also have a real, positive-dollar acquisition and
  still leave common stockholders with nothing if the sale price doesn't
  clear the liquidation preference stack (see the next subsection) — none
  of these datasets report that distinction, so "the company didn't fail"
  is not the same claim as "common stock got paid."
- The underlying data is dated (Correlation's cuts run through 2013;
  CB Insights' post-mortem sample is more current but self-selected)
  relative to the 2021–2023 VC funding boom-and-correction, which several
  practitioner sources argue shifted base rates without, as far as this
  research found, a comparably rigorous re-study.
- Both Correlation Ventures citations are secondary (partner blog posts
  summarizing a VC firm's proprietary numbers), not the underlying
  dataset or a primary published study.

**How to use correctly:** Be explicit with the user, and with whoever
implements `option_value.py`'s exit-probability-haircut defaults (spec
§7, step 3), that this is the single weakest-evidence subsection in this
file. If a flat default is needed, something in the neighborhood of the
convergence across sources — roughly 60–75% of VC-backed positions
returning nothing or less than invested capital to preferred, which likely
understates the true zero-payout rate for *common* once the preference
stack is accounted for — is a defensible order-of-magnitude anchor, but it
should be presented to the user as a rough, unvalidated heuristic, not a
precise probability, and it should not be silently differentiated by
stage (early private / late private / public) since no source here
supports doing so credibly. A future implementer who wants real
stage-differentiated numbers should treat that as open research, not
something already established by this document.

---

### Liquidation Preferences & the Preference Stack

**Source:** National Venture Capital Association (NVCA), Model Legal
Documents / Model Term Sheet, nvca.org (industry-standard template used
across U.S. venture financings). Cooley LLP, *Venture Financing Report*
(quarterly series; Q1 2026 edition checked directly, cooley.com) — an
aggregated survey of deal terms across Cooley's own venture financing
practice. The Holloway Guide to Venture Capital, "Liquidation Preference,"
holloway.com — practitioner reference explaining preference-stack
mechanics.

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
  noted here as an unverified secondary data point roughly consistent
  with Cooley's much higher figure (the discrepancy may reflect different
  denominators — Series A only vs. all rounds — or different report
  vintages).

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

---

### 409A Valuation vs. Preferred Price Gap

**Source:** Moon, C. (2020, February 13). "16 Things to Know About the
409A Valuation." *Andreessen Horowitz (a16z)*, a16z.com. AICPA,
*Valuation of Privately-Held-Company Equity Securities Issued as
Compensation* (Accounting and Valuation Guide / Practice Aid) — the
technical valuation-methodology document (option-pricing method,
probability-weighted expected return method, current value method)
industry-standard 409A appraisers work from. Underlying statutory basis:
Internal Revenue Code §409A (enacted as part of the American Jobs
Creation Act of 2004, post-Enron), which requires an independent,
defensible fair-market-value determination for private-company stock
used to set option strike prices.

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
  lower, on average, is 409A vs. preferred price" — this is the honest
  gap the task brief asked to flag explicitly rather than paper over. The
  best available source (a16z) argues that any single ratio is
  misleading.
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
stage" default — that is precisely the kind of unsupported constant this
research pass could not substantiate, and the one credible source found
warns explicitly against it. If a numeric estimate is genuinely needed,
prefer deriving it from the same residual-claim mechanics already used
for the preference-stack and DLOM subsections (i.e., compute common's
value as a residual after the preference stack, then apply an illiquidity
discount) rather than looking up a stage-based ratio table.

---

### Discount for Lack of Marketability (DLOM)

**Source:** Damodaran, A. (2005, July). *Marketability and Value:
Measuring the Illiquidity Discount* [Working paper]. Stern School of
Business, New York University. pages.stern.nyu.edu (fetched and read
directly). Primary studies synthesized within it: Maher, J.M. (1976).
Discounts for Lack of Marketability for Closely Held Business Interests.
*Taxes*, 54, 562–571. Silber, W.L. (1991). Discounts on Restricted Stock:
The Impact of Illiquidity on Stock Prices. *Financial Analysts Journal*,
47, 60–64. Johnson, B.A. (1999). Quantitative Support for Discounts for
Lack of Marketability. *Business Valuation Review*, 16, 152–155. Wruck,
K.H. (1989). Equity Ownership Concentration and Firm Value: Evidence from
Private Equity Financings. *Journal of Financial Economics*, 23, 3–28.
Hertzel, M. & Smith, R.L. (1993). Market Discounts and Shareholder Gains
from Placing Equity Privately. *Journal of Finance*, 48, 459–486. Bajaj,
M., Dennis, D.J., Ferris, S.P., & Sarin, A. (2001). Firm Value and
Marketability Discounts. *Journal of Corporate Law*, 27. Emory, J.
(1996), reported in Pratt, S., Reilly, R., & Schwiehs, R.P. (1997).
*Valuing a Business: The Analysis and Appraisal of Closely Held
Companies*. McGraw-Hill. Longstaff, F.A. (1995). How Much Can
Marketability Affect Security Values? *Journal of Finance*, 50,
1767–1774.

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
  re-study of restricted-stock or pre-IPO discounts was found in this
  research pass.
- The estimates vary enormously by methodology — from 7.23% (Bajaj et
  al.'s controlled estimate) to 66%+ (Longstaff's upper bound at high
  volatility and a long horizon) — so citing any single number without
  its methodology is misleading.

**How to use correctly:** For `option_value.py`'s time-value/illiquidity
discount default (spec §7, step 4), a range in roughly the **20–30%**
region is a defensible, well-precedented starting point — it's close to
where most of the more carefully controlled empirical estimates (Bajaj et
al.'s 7–28% range depending on control; option-pricing estimates at
1–2 year horizons and moderate volatility, ~17–25%) and the commonly
cited restricted-stock range (20–35%) overlap. But this must be presented
to the user, and documented in the tool, as an explicit rough default
with a defensible range spanning roughly 10–40%+ depending on the
company's actual expected time-to-liquidity and volatility — not a
precise, validated figure. Where possible, the tool should let time
horizon and volatility inputs move the estimate (consistent with the
option-pricing approach) rather than silently applying one flat constant
regardless of the user's actual situation.

---

### ISO vs. NSO Tax Treatment and AMT (flagged, not modeled)

**Source:** National Center for Employee Ownership (NCEO), "Stock Options
and the Alternative Minimum Tax (AMT)," nceo.org/articles (fetched and
read directly; no individual author or date given on the page). Cross-
referenced against the underlying statute: Internal Revenue Code §422
(incentive stock option qualification and statutory holding-period
requirements), §56(b)(3) (ISO exercise spread as an Alternative Minimum
Tax preference item), and §83 (general rule that a nonqualified stock
option's exercise spread is ordinary compensation income).

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

