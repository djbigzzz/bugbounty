# Attack Playbook — derived from bug-bounty winners & consensus/BLS attack literature

Written after round 1 returned zero findings. Round 1 had **three methodological errors**.
This playbook corrects them and defines round 2.

---

## ERROR 1 — Wrong threat model (the big one)

Round-1 agents repeatedly dismissed attacks with *"the attacker would need ≥60% of stake,
that's outside the security model."* **That reasoning is wrong.**

Alpenglow's advertised guarantee is the **"20+20" model**:
- **SAFETY holds with up to 20% Byzantine stake.**
- **LIVENESS holds with a further 20% offline/unresponsive.**

So the bar for a safety finding is: **can 20% of stake break it?** Not 60%. An attacker who
controls 20% of stake controls 20% of *ranks*, can equivocate, restart at will, withhold,
reorder, and craft arbitrary wire messages. Anything that breaks with ≤20% Byzantine stake is
a **violation of the protocol's own claimed guarantee** and is squarely in scope.

**Re-test every round-1 dismissal against a 20% adversary.**

Corollary: the 60% notarize / 80% fast-finalize thresholds mean two conflicting 60% certs
require ≥20% overlap — i.e. exactly at the Byzantine bound. Anything that lets an attacker be
*counted* without genuinely endorsing effectively **lowers the real threshold** and pushes the
system below its claimed tolerance.

## ERROR 2 — "Proof-of-possession, therefore BLS is safe"

PoP defends **rogue-key attacks only**. The literature (eprint 2021/377, IETF BLS draft,
Ethereum beacon-client review) documents attack classes PoP does **not** touch:

| Attack class | Defended by PoP? | What the verifier must do |
|---|---|---|
| Rogue key (`pk_2 = rP − pk_1`) | ✅ yes | PoP over the account-bound message |
| **Small-subgroup / non-prime-order points** | ❌ **NO** | explicit subgroup (`is_torsion_free`) check on every deserialized point |
| **Non-canonical / malleable encodings** | ❌ **NO** | canonical-form check on decompression |
| **Identity / point-at-infinity** | ❌ **NO** | explicit `is_identity` rejection |
| **Splitting-zero / cancellation** | ⚠️ partial | keys summing to zero drop out of the aggregate |
| Cross-message replay | ❌ NO | domain separation per message type |

**Red flag found in the library:** `solana-bls-signatures` ships `PubkeyAffineUnchecked` —
"guaranteed to be a point on the curve, but **not** guaranteed to be in the prime-order
subgroup G1 … designed for efficient *unchecked* deserialization," with `verify_subgroup()`
as an opt-in. **Any remote-input path that builds pubkeys/signatures without a subgroup check
is a candidate finding.** Round 1 never traced these deserialization paths.

## ERROR 3 — Read-only auditing; no PoC attempted

Every bounty platform (and this one explicitly) requires a **reproducing PoC**; reports
without one "are closed as speculative." Round 1 produced zero executable artifacts.
Round 2 must **write and run code** against the real crates — a failing test *is* the PoC.

---

## Winning-submission patterns to imitate

1. **State-lag / restart bypass (HotStuff family).** A node whose local state is lagged (after a
   reboot, snapshot restore, or slow catch-up) accepts a high-view/high-slot certificate that
   bypasses a safety check anchored on that stale state. → Alpenglow analogues: stale `root`,
   restored `vote_history`, `set_identity`, snapshot/repair catch-up, migration handover.
2. **Threshold arithmetic that counts something it shouldn't.** Not off-by-one in the compare —
   double-counting, phantom-counting, or counting across a boundary where the denominator changed.
3. **Two components disagreeing about the same value** (builder vs verifier, leader vs replayer,
   epoch N vs N+1 view of stake/ranks). Divergence = fork.
4. **Malformed wire input** reaching a panic, unbounded allocation, or unchecked deserialization.
5. **Boundary conditions**: epoch transitions, migration cutover, window edges, root advance.

## Round-2 hypothesis queue (each must end in runnable code)

- **H1 (crypto/deserialization):** any remote BLS pubkey/signature deserialized without subgroup
  or canonical-encoding validation → forgery/DoS. *Trace every wire→point conversion.*
- **H2 (20% safety):** with exactly 20% Byzantine stake, construct two conflicting certs, or a
  cert counted at 60% with only 40% genuine endorsement. Cancellation makes the attacker
  *counted without signing* — quantify whether that lowers the effective threshold or destroys
  equivocation evidence (accountability), and whether the protocol claims accountability.
- **H3 (state-lag):** validator restarts / restores a snapshot with stale root & vote history,
  then receives certs for far-higher slots. Can it be induced to vote conflicting, root a
  non-finalized block, or skip a safety check anchored on the stale value?
- **H4 (fuzz/DoS):** fuzz `decode()`, cert/vote deserialization, and `verify_certificate` with
  malformed bitmaps and points. Target panics, OOM, quadratic blowups on unauthenticated input.
- **H5 (epoch boundary):** cert produced in epoch N verified against epoch N+1's rank map or
  total_stake; stake/rank changes at the boundary; leader-schedule straddle.

**Standard of proof:** CONFIRMED = a test that runs and demonstrates the impact at commit
`f01d78d`, still unfixed on master. Nothing below that gets a 0.5 SOL burn.
