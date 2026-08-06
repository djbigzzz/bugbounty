# Alpenglow Audit — Findings Log

Cited commit: `f01d78db8a89c36bee025cda13413e1bdca1fb50` (master HEAD, 2026-08-06).
Status legend: 🔴 submit-candidate · 🟡 needs verification · ⚪ latent/non-exploitable · ✅ verified sound (negative result).

Nothing here is submission-ready until it has a **reproducing PoC** and passes the REPORT_TEMPLATE pre-flight checklist. We only burn 0.5 SOL on 🔴 items with a working PoC.

---

## Area 1 — Certificate & signature verification  (agent: cert/sigverify) — RETURNED, re-running on identity lead
- ⚪ **F1: `AggregateAccumulator::add_aggregate` adds stake unconditionally while OR-ing rank bits.** If overlapping ranks ever reached it, stake would double-count and a locally-built cert could cross threshold on inflated stake. Not remotely reachable today — every upstream path dedups (bls-sigverify `VotePool` rejects repeated `(rank,type,block)`; external aggregates attributed only to gossip sender's own rank). Receivers unaffected (they recompute stake from the bitmap). *Recommend a dedup guard; latent hazard, not a submission.* `votor/src/aggregate_accumulator.rs:57-67`
- ✅ Threshold math, epoch binding (build==verify use same lookup), domain separation (type tag + shred_version in every payload), `PopVerified::new_unchecked` chain, empty-set → error, reward-cert credited set = HashSet backed by verifying sig. All verified sound.
- 🟡 **OPEN (priority):** does the *verifier* reject an identity-signature certificate? The builder-side fix `71e6c74` landed mid-window; verifier parity is being checked now.

## Area 4 — Migration & wire format  (agent: migration) — RETURNED
- ⚪ **M-vs-G dual migration-slot definition.** `MigrationStatus` uses M = activation_slot + MIGRATION_SLOT_OFFSET(5000); `Bank::get_alpenglow_migration_slot` uses G = genesis_cert.block.slot (< M). They derive to different epochs only if M crosses an epoch boundary G does not. The 5000-slot offset is designed to keep migration away from boundaries, so on realistic params `get_epoch(G)==get_epoch(M)` and they coincide; even in the contrived straddle the behavioral delta is minor (legacy TowerBFT thread shutdown, not consensus). Sibling of known #14207 but a distinct location. *SPECULATIVE, likely non-exploitable.* `votor-messages/src/migration.rs:407,414-415`; `runtime/src/bank.rs:6701-6704`; `runtime/src/alpenglow_epoch_type.rs:156-159`
- ✅ Wire format re-derives the signed bytes from `(Vote, shred_version)` rather than trusting wire bytes → no malleability/forgery; unknown tags rejected; shred_version validated at decode and bound into every payload → no cross-cluster/fork replay.
- ✅ Genesis threshold 82% (`migration.rs:88`); two conflicting 82% genesis certs need 64% double-voters vs a 20% fault budget — infeasible. Cutover trigger deterministic (M derived from consensus-agreed activation slot). Genesis cert bound to `(slot,block_id)`, not replayable.
- ✅ Migration "cannot recover" panics all require an already-verified 82% genesis cert or internal error — not remote-reachable. Deserialization allocations bounded.
- ❗ Handoff: did **not** trace `block_component_processor/vote_reward.rs` lamport math end-to-end (loss-of-funds class) — flagged for the rewards agent.

## Area 2 — Consensus pool & vote accounting  (agent: consensus-pool) — running
## Area 3 — Votor event loop, timers, voting  (agent: event-loop) — running
## Area 5 — Reward certs & validator admission  (agent: rewards) — running
## Area 6 — Network integration points  (agent: networking) — running
