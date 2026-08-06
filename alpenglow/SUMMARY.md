# Alpenglow Bug Bounty — Audit Scoreboard

**Target:** `anza-xyz/agave` @ `f01d78db8a89c36bee025cda13413e1bdca1fb50` (master HEAD, 2026-08-06)
**Window:** 2026-08-05 → 2026-08-19 · **Portal:** alpenglow.anza.xyz (0.5 SOL burn per report)
**Method:** 6 parallel specialist audits + BLS-library source verification. Details in `FINDINGS_LOG.md`.

## Headline count — confirmed, submittable, PoC-backed findings

| Severity (bounty tier) | ≈ Class | Reward band (SOL) | **Confirmed** | Under verification | Latent / hardening |
|---|---|---|:--:|:--:|:--:|
| Loss of Funds | Critical | 6,250 – 25,000 | **0** | 0 | 0 |
| Consensus / Safety | Critical / High | 3,125 – 12,500 | **0** | 0 | 2 |
| Liveness | High / Medium | 1,250 – 5,000 | **0** | **1** | 1 |
| DoS | Medium / Low | 315 – 1,250 | **0** | 0 | 1 |
| Informational / hardening | Info | — | — | — | 3 |
| **Total** | | | **0** | **1** | **7** |

> **Confirmed = 0.** Nothing is PoC-proven and submittable yet. One liveness lead is still being
> verified; everything else resolved to latent/non-exploitable or a hardening note. We do **not**
> burn 0.5 SOL on anything below "Confirmed + reproducing PoC."

## Findings inventory (everything surfaced, honestly graded)

| # | Finding | Area | Assessed | Exploitable? | Disposition |
|---|---|---|---|---|---|
| 1 | Unaligned-migration partial window has no crashed-leader skip timer | Network / Votor | Liveness (if real) | **Under verification** | Event-loop agent tracing `SafeToSkip`/standstill; wedge only if withholding leader + no other skip path |
| 2 | Non-fsync `vote_history` persist → self-equivocation after power loss | Event loop | Safety-flavored | Power-loss-gated, not remote | HOLD — likely TowerBFT-parity ⇒ out of scope; verify before any burn |
| 3 | BLS identity-cancellation → below-threshold certificate | Cert-verify / pool / crypto | Safety (if real) | **No** (resolved 3 ways) | Closed: lib rejects identity aggpk + PoP caps to attacker's own stake |
| 4 | Slashing-accountability nuance from key-cancellation | Cert-verify | Speculative | Not a threshold break | Flag to votor/slashing owner; out of audited files |
| 5 | M-vs-G dual "migration slot" definition (epoch straddle) | Migration | Latent | Non-exploitable on real params | Vendor hygiene note |
| 6 | `try_build_base2_cert` missing `#14390` `is_identity` guard | Consensus pool | Hardening | No (needs ≥threshold attacker set) | Defense-in-depth; sibling of the mid-window fix |
| 7 | `add_aggregate` unconditional stake add (no dedup guard) | Cert-verify / pool | Hardening | No (all upstream paths dedup) | Latent-fragility note |
| 8 | `add_genesis` skips the `slot<=root` guard | Consensus pool | Informational | No (migration-only) | Inconsistency note |

## Coverage — what was audited and the verdict

| Area | In-scope crates/files | ~LOC | Verdict |
|---|---|--:|---|
| Cert & signature verification | `bls-cert-verify`, `bls-sigverify`, `votor-messages` verify/wire | ~10k | ✅ Sound |
| Consensus pool & vote accounting | `votor/consensus_pool*`, `aggregate_accumulator` | ~8k | ✅ Sound |
| Event loop / timers / voting | `votor/event_handler`, `timer_manager`, `vote_history` | ~13k | ✅ Sound (1 durability note) |
| Migration & wire format | `votor-messages/migration`, `wire`, `alpenglow_epoch_type` | ~3k | ✅ Sound (1 latent note) |
| Reward certs & admission (loss-of-funds) | `runtime` reward/VAT path, `block_component` | ~4k | ✅ Solid (high confidence) |
| Network integration points | repair, `retransmit`, `window_service`, `replay_stage`, rooting | ~6k | ✅ Sound (1 open lead) |

## Context that shapes the result
- **7 hardening commits landed *inside* the competition window** (some hours before our snapshot) — the
  team is actively patching the exact bug classes hunted. Fresh code is immediately in scope; each was
  audited and the flagged fixes (`b29a479`, `ee52e3b`, `71e6c74`) verified complete.
- **12 known issues** (`consensus-team`/`blocking-ag` labels) are ineligible and were excluded; several
  were used as maps to hunt unfixed siblings (none found submittable).
- A rigorous **verified-negative** on freshly-hardened consensus code is the expected outcome of a
  competent audit here — reported as such rather than inflated into a speculative burn.

*Legend: ✅ verified sound · Confirmed = reproducing PoC + still-unfixed on master · Latent = real code smell, not remotely reachable · counts update when the open lead resolves.*
