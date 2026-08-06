# Alpenglow Bug Bounty — Shared Audit Brief

**Target repo (local clone):** `/home/user/agave`
**Cited commit (master HEAD):** `f01d78db8a89c36bee025cda13413e1bdca1fb50` (2026-08-06)
**Window:** 2026-08-05 16:00 UTC → 2026-08-19 16:00 UTC
**Portal:** https://alpenglow.anza.xyz/ (0.5 SOL non-refundable burn per finding)

## The governing in-scope test

> A fault counts **only if it occurs because the Alpenglow feature is active**, wherever in the tree it lives.

### Fully in scope (core crates)
- `votor/` — event loop, consensus pool, vote aggregation, certificate builder, rooting
- `votor-messages/` — certificate/vote/consensus-message serialization, migration handover
- `bls-sigverify/` — BLS vote & certificate signature verification
- `bls-cert-verify/` — certificate verification & stake-threshold checks

### In scope where touching the Alpenglow path
- `core/src/cluster_info_vote_listener.rs` — gossip vote ingestion
- `core/src/block_creation_loop/rewards/` — certs_builder, reward_certs_service, certs_requestor
- `runtime/src/validated_reward_certificate.rs`, `runtime/src/validated_block_finalization.rs`
- `runtime/src/epoch_stakes.rs` — BLS-pubkey rank map and voter set
- `runtime/src/block_component_processor.rs` + `block_component_processor/vote_reward.rs`
- `entry/src/block_component.rs` — structure and parsing
- `runtime/src/alpenglow_epoch_type.rs` — epoch-type semantics
- `runtime/src/bank.rs` — validator-admission (VAT) enforcement
- `runtime/src/bank_forks.rs` — rooting integration
- `core/src/repair/{block_id_repair_service,repair_handler,serve_repair}.rs` — chained repair
- `core/src/replay_stage.rs`, `core/src/replay_stage/update_parent.rs` — Votor integration, fast-handover markers
- `ledger/src/blockstore_processor.rs` — UpdateParent replay, fast-leader-handover gating
- `turbine/src/retransmit_stage.rs` — FirstShred event into Votor
- `core/src/window_service.rs` — duplicate-shred & chained-merkle-root handling

BLS aggregation/verification **misuse** is in scope. Bugs inside `blst`/BLS12-381 itself are **out**.

### Explicitly OUT of scope
- Non-Alpenglow startup/wiring: `core/src/{validator,tvu,tpu,admin_rpc_post_init}.rs`, top-level `block_creation_loop.rs` orchestration
- TowerBFT-only: `consensus.rs`, `commitment_service.rs`, `replay_stage/dead_slots.rs`
- Leader-only emission: `turbine/src/broadcast_stage.rs`
- Any path reachable only with `alpenglow` **inactive**; scaffolding behind inactive features
- Test code, `core/src/banking_simulation.rs`
- Standing `SECURITY.md` exclusions: metrics, dependencies, snapshots, bootstrap config, RPC, social engineering, Loader-V4, geyser/scheduler-bindings
- Anything already public or in the known-issues tracker

## Severity rubric (assessed severity governs, not claimed)

| Severity | Definition | Award (SOL) | Unlocks pool |
|---|---|---|---|
| **Loss of Funds** | Theft/unauthorized movement. Usually a safety violation enabling double-spend, or a reward/credit bug misallocating stake or rewards. | 6,250–25,000 | 50,000 |
| **Consensus / Safety** | Safety break w/o fund impact: two conflicting blocks notarized/finalized, cert accepted **below required stake threshold**, contradictory finality, acceptance of equivocating votes that should be rejected. | 3,125–12,500 | 30,000 |
| **Liveness** | Consensus halts, needs human intervention: cert can never form for an honest leader, permanent skip-vote cascade or deadlock, partition, eclipse. | 1,250–5,000 | 20,000 |
| **DoS** | Remote resource exhaustion/degradation via non-RPC protocols, not halting consensus; recoverable stalls; block delayed well beyond target slot time. | 315–1,250 | 10,000 |
| **Other** | Reproduced impact outside the above. **Never self-assign** — self-selecting Other will almost certainly disqualify. | Discretionary | — |

Multiple findings at one level do not raise the ceiling. If total awards exceed the unlocked pool, all are cut pro-rata.

## Hard submission requirements
1. **A reproducing PoC is required at every severity** — local fork, multi-node harness, or simulation. **Never** mainnet or public testnet. Must demonstrate the claimed impact **at the cited commit**, with mechanism, adversary model, and steps. No PoC ⇒ "closed as speculative."
2. Finding must be present at the cited in-window `master` commit **and still unfixed on `master` at submission time**. A fix landing first makes it retroactively ineligible.
3. One finding per GitHub Security Advisory, via the portal only.
4. **No public disclosure anywhere** — instant ineligibility.
5. Duplicates: entire reward to the earliest report substantiating the issue at its assessed severity. Speed + rigor beats severity inflation.

SLAs: first response 72h, initial severity call 7 days, final adjudication by 2026-09-02.
Payout: lump sum post-adjudication, after KYC, in **12-month locked SOL**. OFAC-sanctioned jurisdictions ineligible.

## What a good finding looks like here
Not a lint. We want a violated **invariant**, e.g.:
- A certificate accepted whose aggregate stake is genuinely below the type's threshold (60% notarize/skip/finalize, 80% fast-finalize)
- Stake double-counted across primary/fallback bitmaps, or across epochs
- A cert verified against the **wrong epoch's** `total_stake` or rank map
- Two conflicting blocks both reaching notarization/finalization
- Equivocating votes accepted where the protocol requires rejection
- Reward certificates crediting stake that did not vote (loss of funds)
- A state machine that can wedge permanently (no cert can ever form)
- Unauthenticated remote input causing panic/unbounded allocation on the Alpenglow path
