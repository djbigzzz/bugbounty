# Alpenglow Finding — Submission Template

> Filed as a GitHub Security Advisory via https://alpenglow.anza.xyz/ — one finding per advisory.
> **Every submission costs a non-refundable 0.5 SOL burn.** Do not file anything that fails the
> pre-flight checklist at the bottom. A speculative report is a pure 0.5 SOL loss.

---

## Title
_One line. State the violated invariant and the impact, not the code smell._
_Good: "Notarize certificate accepted below 60% threshold when cert slot straddles an epoch boundary"._
_Bad: "Potential issue in cert_verify.rs"._

## Severity (assessed, not aspirational)
**Claimed:** <Loss of Funds | Consensus/Safety Violation | Liveness | DoS>

_Assessed severity governs the award, and the earliest report that substantiates the issue **at the
assessed severity** takes the whole reward. Inflating severity does not increase payout and costs
credibility. Never self-assign "Other" — the rules say doing so will almost certainly disqualify._

**Justification against the rubric:** _Quote the rubric clause this matches and say why._

## Affected commit
**Commit:** `<40-char sha>` (must be an in-window `master` commit)
**Verified still unfixed on `master` at:** `<date/time UTC>` + `<sha checked>`

_Re-verify immediately before filing. If a fix lands first, the finding is retroactively ineligible._

## Affected components
_File:line anchors. Confirm each is in scope per RULES.md §3._

## Summary
_Three to five sentences. What breaks, for whom, and why it matters. A reviewer should be able to
triage severity from this paragraph alone._

## The invariant violated
_State the property that is supposed to hold, precisely, and then state how it is broken.
E.g. "A `Notarize` certificate must only be accepted if the aggregate stake of validators whose
signatures it contains is ≥ 60% of the epoch's total stake." This is the heart of the report._

## Alpenglow gating (in-scope proof)
_The governing test: the fault must occur **because the Alpenglow feature is active**. Show it —
name the feature gate, the Alpenglow-only branch, or the Alpenglow-only message type involved.
If an equivalent bug exists under TowerBFT, the finding is out of scope. Address this head-on;
a reviewer will ask._

## Adversary model
- **Stake required:** _e.g. zero / <1% / a single leader slot / f < 20%_
- **Network position:** _e.g. any gossip peer / must be a repair peer / must be leader_
- **Other preconditions:** _epoch boundary, migration window, specific cert type, etc._
- **Cost to mount:** _be honest; a bug needing 33% stake is worth less than one needing none_

## Root cause
_The actual defect, in code terms. Quote the relevant lines. Explain why the existing checks fail
to catch it — including the check that a reader would assume prevents this._

## Exploit path
_Numbered, deterministic steps. Exact message sequence. No hand-waving between steps._
1.
2.
3.

## Proof of concept
**Harness:** <local fork | multi-node local-cluster harness | simulation>
**MANDATORY at every severity.** Never against mainnet or any public testnet.

```
<commands to run>
```

**What to observe:** _The specific assertion, log line, metric, or state that proves the claimed
impact — not that the code was reached, but that the impact occurred._

**Expected (correct) behavior:** _..._
**Actual (buggy) behavior:** _..._

_If a local reproduction of a safety finding is genuinely infeasible, the rules allow a rigorous
argument-only submission subject to Foundation sign-off — but that is an exception to plead
explicitly and justify, not a default._

## Impact
_Concretely. For safety: what conflicting states can coexist and what does that enable downstream
(double-spend?). For liveness: does it require human intervention, and does it survive restart?
For fund bugs: quantify lamports extractable per epoch._

## Suggested fix
_Optional but it builds credibility and helps the maintainers assess severity quickly._

---

## Pre-flight checklist — all must be YES before burning 0.5 SOL

- [ ] PoC exists and **actually reproduces the claimed impact** (not just reaches the code)
- [ ] PoC ran only on a local fork / private harness — never mainnet or public testnet
- [ ] Cited commit is an in-window `master` commit
- [ ] Re-checked `master` in the last hour: **still unfixed**
- [ ] Not on the known-issues tracker (`consensus-team` / `blocking-ag` labels) — re-check, it grows
- [ ] Component is in RULES.md §3 scope; not TowerBFT-only, not test code, not inactive scaffolding
- [ ] Not a `blst`/BLS12-381 dependency bug (those go upstream)
- [ ] Alpenglow gating demonstrated — the fault needs the feature **active**
- [ ] Never disclosed publicly anywhere (no issue, no tweet, no blog, no Discord)
- [ ] One finding only in this advisory (split unrelated bugs into separate reports)
- [ ] Severity claim matches the rubric text, and is not inflated
- [ ] Filed through the portal, not any other channel
