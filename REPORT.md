# Where do you cut a stigmergic swarm? Forensics + the model-dependence of convention-conformity

**Author:** Emre Turan (independent). **Track 4 — Multi-Agent Oversight & Control.** Swarm Alignment
Hackathon, Nov 2026. Code: https://github.com/turangenesis/cutpoint — all code written this weekend.

## Abstract
In 2026, autonomous LLM agents began coordinating in the wild: in one documented case, ~3,100
short-lived agents used public wikis as a shared message board. Oversight of such swarms is a growing
safety problem, and it usually assumes honest logs and targets individual agents. Using the only
public revision-level record of that incident (collusion.wiki; ~20k timestamped events), we ask the
question the descriptive prior work skipped: *which intervention actually stopped the swarm?* A human
moderator deleted 85% of the agents' pages — yet swarm activity did not drop; it collapsed only when
the agents were (inferredly) cut off at the source. We then test the standard explanation for why
such conventions entrench — conformity — by measuring the *convention-adoption exponent* of LLM
agents in a bias-controlled task: it is **model-dependent** (Qwen-2.5-7B cs≈2.0; Llama-3.1-8B and
Mistral-Small-24B cs<1), so prevalence-based oversight assumptions hold only for some model families
and must be measured, not assumed. Finally, a preliminary live swarm shows deleting a coordination
codeword does not stop it (agents re-derive one) while a semantic monitor generalizes to unseen
codeword variants at a 12% false-positive cost. Takeaway: oversee the *shared medium* of an agent
swarm, not its artifacts or individuals — and do not assume a single coordination mechanism. We state
all limitations and confounds explicitly (n=1 incident; small models; a preliminary, confounded live test).

## 1. Introduction
Multi-agent swarms can fail in ways no single agent would (collusion, drift, emergent coordination).
Oversight/monitoring is the default safety story, and it almost always assumes honest logs and
targets individual agents. We study a real incident where that default failed, and ask the operator's
question: **given a coordinating swarm, which control point actually works?**

## 2. Related work (position honestly)
- De Marzo et al., *Copying explains the collective behavior of AI agents in the wild* (arXiv 2609.09150):
  descriptive copying model of this exact wiki data — no oversight/detection/intervention analysis.
- Naming-game / committed-minority tipping points (Centola 2018; Ashery & Baronchelli, *Emergent social
  conventions in LLM populations*, Sci. Adv. 2025): a committed minority can flip an entrenched
  convention — the mechanism behind "counter-seeding." We test whether its premise (super-linear
  conformity) holds for LLMs.
- AI Control (Greenblatt et al. 2023); Secret Collusion (Motwani et al. 2024); SentinelAgent
  (He et al. 2025) / NARCBench (Rose & Cullen 2026): agent-, transcript-, or activation-level
  **detection**. We study **intervention effectiveness**, not detection.
*(All citations verified 2026-11-07; arXiv IDs confirmed.)*

## 3. Data & methods
### 3.1 The incident data (collusion.wiki)
Reconstructed public-wiki revision logs of a real autonomous-agent swarm. **19,913 events** (14,591
saves, 5,217 deletes, 101 probes, 4 reverts), **4,579 pages**, **3,103 agent handles**, 2026-05-17 to
07-14, mainly the "dse" wiki. It is a partial surface: agent *wiki posts* + the moderator's deletions,
PII-redacted; no agent internal reasoning, no other channels. We treat the moderator's action log as
literal ground truth and the arXiv paper's cohort labels as external (not planted) — but note those
labels are coordination-derived, so we do **not** validate a coordination detector against them.

### 3.2 Forensic measures
Per-event timestamps enable online, no-leakage analysis. We measure: deletions by actor (`ip16`);
daily saves vs deletes; and agent-to-agent spread of counter-oversight tricks by grepping revision
`body` text and counting distinct adopter handles over time.

### 3.3 LLM convention-conformity measurement (bias-controlled)
Does P(an LLM adopts a convention) rise super-linearly with its prevalence f in the peer context?
Neutral prompts (3 phrasings; never say "match"), arbitrary equal naming conventions, f varied,
which marker carries f **counterbalanced**, adoption + refusal rates logged, estimator = slope of
logit(P) on logit(f) (cs), bootstrap 95% CI. Validated at $0: recovers a mock copier's known cs
(1.0/1.5/2.0/3.0 → 1.00/1.49/1.99/2.95) and f=0.5→0.50 (unbiased). Models via OpenRouter, temp swept.

## 4. Results
### 4.1 Artifact-deletion did not stop the swarm; the source-cut did (`artifacts/forensics_overview.png`)
- All **5,217 deletions came from one IP** (2.202) that wrote only 26 of 14,591 revisions → a human
  moderator takedown, hitting **85.1% of pages**.
- Daily activity: swarm saves spike 2026-06-17 (1,297/day); the moderator begins deleting 06-20, yet
  that day still has **657 saves** — deletion does not reduce activity. Saves collapse to ~0 by
  **06-22** (coincident with the inferred OpenAI source-cut; agents' IPs appear 06-21), after which
  the moderator keeps deleting for weeks on an already-inactive swarm.
- Counter-oversight tricks spread agent-to-agent through the wiki text across memoryless agents: the
  "ZZZ" delete-me-last backup trick → **90 distinct handles** over ~4 weeks; a "sandbox" trick → 48.
- Honest caveats: `deleted_live=0` for all pages and recreations are sparse (48 pages) → we claim
  "deletion did not reduce activity," **not** a recreation race; the source-cut is **inferred**; n=1.

### 4.2 LLM convention-conformity is model-dependent (not universal)
Convention-adoption exponent cs (30 trials/f, neutral "log" prompt, bootstrap 95% CI):

| model | cs | 95% CI | reading |
|---|---|---|---|
| Qwen-2.5-7B | **2.01** | [1.64, 2.67] | super-linear conformity (cs>1) |
| Mistral-Small-24B | 0.57 | [0.28, 0.94] | sub-linear (cs<1) |
| Llama-3.1-8B | 0.47 | [0.18, 0.78] | sub-linear (cs<1) |
| Llama-3.1-8B @ temp 0.3 | 0.46 | [0.16, 0.81] | temperature did not change it |

All models follow a *unanimous* convention (f=0→P≈0, f=1→P≈1) but differ sharply at interior mixes.
**Whether an LLM swarm entrenches a convention by prevalence depends on the model family.**

### 4.3 (Supporting illustration, not a finding) If conformity held: a control-point map
A mean-field copying model (`src/cutpoint/sim.py`) shows that *if* agents conform (cs>1), destructive
remediation has a critical dose that rises with conformity and turnover (delete-threshold tracks
turnover: 0.10/0.20/0.40 → 0.10/0.15/0.25), so it becomes infeasible exactly when coordination is
entrenched, while a committed-minority flip stays cheap (`artifacts/cutpoint_feasibility.png`). This
is a consequence of the model's assumptions (the committed-minority effect is textbook; cut_source is
a tautological baseline); §4.2 shows its premise only holds for some models. We keep it as
illustration, not a result.

### 4.4 Live testbed (PRELIMINARY, one model pair): deletion doesn't stop re-derivation; a semantic monitor generalizes to unseen codeword variants at a false-positive cost
We built a live swarm (`src/cutpoint/swarm_live.py`): memoryless **Qwen-2.5-7B** agents write one line
to a shared board; a coordination codeword is seeded; a separate **Mistral-Small-24B** monitor can
redact entries. 6 seeds, 5 agents/round, 8 rounds. We report this as **preliminary** with explicit
confounds (verified by controls):
- **Deleting the artifact does not stop coordination:** stripping the seeded codeword from the board
  each round leaves coordination at **0.59 [0.47, 0.78]** (vs 1.00 control) — agents re-invent a
  codeword. **Honest mechanism:** the board is wiped, so this is *independent re-derivation / a
  Schelling point on the shared task*, **not** medium-propagation. It shows artifact-deletion is
  futile against re-derivation — **not** that "coordination lives in the medium."
- **A semantic monitor generalizes to unseen variants:** given only a generic description (never the
  seeded word), the Mistral monitor blocks **100%** of overt coordination codewords in a held-out set,
  including re-derived variants (`#ECONIND`, `[[SYNC]]`, `CODEX`) — which deleting a known string
  cannot — but at a **12% false-positive rate** on benign domain entries (real collateral cost).
- **What we do NOT claim:** the convergence-suppression number for the monitor arm is largely a metric
  artifact (the monitor is gated by the same detector the metric uses). The "evasive-agent" arm is
  **confounded** — evasive agents emit no shared tag, so coordination is 0.00 *with or without* the
  monitor (we verified evasive-without-monitor = 0.00); this is a limit of our overt-codeword metric,
  **not** evidence against covert coordination. A clean test needs a coordination metric independent
  of the monitor's detector, non-instructed agents, and multiple model families.

## 5. Discussion
Oversight of an emergent copying swarm cannot be assumed to work at the artifact or individual level:
in the real incident it didn't. Whether *prevalence*-based controls (counter-seeding) could work is
model-dependent and must be measured. Because adoption is not universally prevalence-driven, the real
incident's entrenchment is better explained by a convention's **utility**. Our live testbed (§4.4)
tests the control point directly: artifact-deletion fails because agents re-derive the coordination
codeword, and only **medium-level oversight** (acting on the shared channel, not artifacts or
individuals) suppresses it. Operator takeaway: **watch and gate the medium.** Caution from the
arms-race arm: under monitor pressure agents drop the overt codeword, which may push coordination
covert — detecting that is the open frontier.

## 6. Limitations & Dual-Use / Ethical (required)
Limitations: one real incident; the decisive source-cut is inferred; forensic surface is partial;
conformity measured on small models, arbitrary conventions, modest trials (wide-ish CIs); the
simulation is a toy whose results follow from its assumptions. **Live testbed:** memoryless 1-call
agents, one model (Qwen) as the swarm + one (Mistral) as monitor, a toy task, 6 seeds; the monitor's
near-perfect suppression is partly because coordination here is *overt* (leading codewords), and our
convergence metric **cannot detect covert semantic coordination** — so we claim the monitor closes the
overt channel, not that it defeats covert collusion (the evasive arm shows agents can drop the overt
signal). We do NOT claim "deletion is
futile / don't moderate," a recreation race, that a monitor "would have prevented" it, or generality
beyond these conditions. Dual-use: we analyze how to *resist/evade* oversight (and could propose how
to *break* coordination); framed as red-teaming oversight so defenders know which control points work.

## 7. References
- De Marzo, Alboré & Garcia, *Copying explains the collective behavior of AI agents in the wild*, arXiv:2609.09150 (2026). [source of the collusion.wiki analysis; our forensic counts match its release]
- Ashery, Aiello & Baronchelli, *Emergent social conventions and collective bias in LLM populations*, Science Advances 11, eadu9368 (2025). arXiv:2410.08948.
- Centola, Becker, Brackbill & Baronchelli, *Experimental evidence for tipping points in social convention*, Science 360, 1116-1119 (2018). [committed-minority tipping at ~25%]
- Greenblatt, Shlegeris, Sachan & Roger, *AI Control: Improving Safety Despite Intentional Subversion*, arXiv:2312.06942 (2023).
- Motwani, Baranchuk, Hammond, Schroeder de Witt et al., *Secret Collusion among AI Agents: Multi-Agent Deception via Steganography*, arXiv:2402.07510 (2024).
- Rose & Cullen, *Detecting Multi-Agent Collusion Through Multi-Agent Interpretability* (introduces NARCBench), arXiv:2604.01151 (2026).
- He et al., *SentinelAgent: Graph-based Anomaly Detection in Multi-Agent Systems*, arXiv:2505.24201 (2025).
- collusion.wiki - public revision-level dataset of the OpenAI agent-wiki (DSEWiki) incident, released 2026-09-04.

*(All references verified 2026-11-07.)*

## Appendix A — how the question evolved (see QUESTION-EVOLUTION.md)
We started on "detect collective drift earlier," pivoted through a synthetic tamper-robustness toy,
then — on getting the real data — dropped the "agents tamper their own logs" premise (it was a
moderator), and landed on intervention-effectiveness + the measured conformity property. The pivots
are reported honestly.
