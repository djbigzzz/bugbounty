# Alpenglow Bug Bounty — Audit Scoreboard

**Target:** `anza-xyz/agave` @ `f01d78db8a89c36bee025cda13413e1bdca1fb50` (master HEAD, 2026-08-06)
**Window:** 2026-08-05 → 2026-08-19 · **Portal:** alpenglow.anza.xyz (0.5 SOL burn per report)
**Method:** 6 parallel specialist audits + BLS-library source verification. Details in `FINDINGS_LOG.md`.

## Headline count — confirmed, submittable, PoC-backed findings  ·  AUDIT COMPLETE

| Severity (bounty tier) | ≈ Class | Reward band (SOL) | **Confirmed** | Latent / hardening | Resolved safe |
|---|---|---|:--:|:--:|:--:|
| Loss of Funds | Critical | 6,250 – 25,000 | **0** | 0 | 1 |
| Consensus / Safety | Critical / High | 3,125 – 12,500 | **0** | 4 | 1 |
| Liveness | High / Medium | 1,250 – 5,000 | **0** | 1 | 1 |
| DoS | Medium / Low | 315 – 1,250 | **0** | 1 | 0 |
| Informational / hardening | Info | — | — | 1 | — |
| **Total** | | | **0** | **7** | **3** |

> **Confirmed = 0.** No PoC-provable, submittable vulnerability was found at this commit. All six
> areas and every lead — including the one liveness thread held open longest — resolved to
> verified-sound, latent/non-exploitable, or a hardening note. We do **not** burn 0.5 SOL on
> anything below "Confirmed + reproducing PoC," so **no submission is recommended** from this pass.

## Findings inventory (everything surfaced, honestly graded)

| # | Finding | Area | Assessed | Exploitable? | Disposition |
|---|---|---|---|---|---|
| 1 | Unaligned-migration partial window "has no crashed-leader skip timer" | Network / Votor | Liveness | **No — resolved SAFE** | Premise false: `consensus_pool_service.rs:301` emits `ParentReady(G+1)` un-gated → timers arm whole partial window → `try_skip_window` skips it → parent-ready advances. Verified G=5,6,7 |
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
| Network integration points | repair, `retransmit`, `window_service`, `replay_stage`, rooting | ~6k | ✅ Sound |

## Context that shapes the result
- **7 hardening commits landed *inside* the competition window** (some hours before our snapshot) — the
  team is actively patching the exact bug classes hunted. Fresh code is immediately in scope; each was
  audited and the flagged fixes (`b29a479`, `ee52e3b`, `71e6c74`) verified complete.
- **12 known issues** (`consensus-team`/`blocking-ag` labels) are ineligible and were excluded; several
  were used as maps to hunt unfixed siblings (none found submittable).
- A rigorous **verified-negative** on freshly-hardened consensus code is the expected outcome of a
  competent audit here — reported as such rather than inflated into a speculative burn.

## Final recommendation
**No submission from this pass.** Zero confirmed, PoC-backed, in-scope vulnerabilities at `f01d78d`.
The consensus/crypto core is well-engineered and was hardened by 7 in-window commits; the deepest
lead (BLS identity-cancellation) and the most stubborn liveness thread (migration partial-window)
both resolved to sound. The right deliverable here is this rigorous **verified-negative with reasons**,
not a speculative 0.5-SOL burn. If the hunt continues, the only non-trivial residual worth a decision
is finding #2 (vote-history durability) — and only after confirming it is not TowerBFT-identical
(which would put it out of scope).

*Legend: ✅ verified sound · Confirmed = reproducing PoC + still-unfixed on master · Latent = real code smell, not remotely reachable · Resolved safe = hypothesised bug traced and disproven.*
