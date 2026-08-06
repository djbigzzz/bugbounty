# Known Issues — OUT OF SCOPE (ineligible)

Tracker (from the bounty README): `anza-xyz/agave` issues labeled `consensus-team` or `blocking-ag`
https://github.com/anza-xyz/agave/issues?q=is%3Aissue+label%3Aconsensus-team%2Cblocking-ag

Snapshot taken 2026-08-06. **Re-check before every submission** — the list grows, and a finding that
lands on this tracker before we submit becomes retroactively ineligible.

Note the tracker is NOT the `alpenglow` label (that label has zero issues and is a red herring).

| # | Title | State | Area |
|---|---|---|---|
| 14335 | Reduce the bound of vote ingest in BLS sigverify | Closed | sigverify DoS |
| 14300 | Replace evicting sender with a retry queue for own votes | Open | own-vote delivery |
| 14299 | VOTOR_RATE_LIMIT_PPS should scale with slot duration | Open | rate limiting |
| 14298 | votor: a valid 5th notar-fallback certificate may panic the consensus-pool thread | Closed | cert handling panic |
| 14282 | Front-load cheap checks during certificate verification | Open | cert verify DoS |
| 14208 | alpenglow: two ASN parsers | Open | parser divergence |
| 14206 | alpenglow: votor event channel can deadlock the consensus loop | Closed | liveness deadlock |
| 14207 | alpenglow: Migration epoch derived from activation slot instead of migration slot | Closed | migration |
| 14205 | alpenglow: FecSetRoot repair accepts an empty Merkle proof | Closed | repair validation |
| 14194 | alpenglow: Missing check may lead to removal of Bank queued to be rooted | Closed | rooting |
| 14159 | Fast-handover replay hard-deads a malformed optimistic prefix that UpdateParent accepts | Closed | SIMD-0337 handover |
| 14211 | vote-only mode not enforced on startup/blockstore replay path | Closed | activation |

## How to read this list offensively

These 12 are excluded, but they are the most useful document in the whole bounty. They tell us
**which bug classes actually exist in this codebase** and where the maintainers' own review found
problems. The hunt is for *unfixed siblings* of these:

- **#14298** proves notar-fallback certificate counting has panic-reachable edge cases tied to the
  "at most N fallback certs" logic. Are there sibling panics for skip-fallback, or at other counts?
- **#14206** proves the event channel can deadlock. Deadlock was found once in this state machine;
  look for other channel/lock cycles, especially ones that survive restart.
- **#14205** proves repair accepted a structurally-empty proof. Look for other "empty/degenerate
  input passes validation" cases — empty bitmaps, zero-length proofs, empty pubkey sets.
- **#14194** proves rooting had a missing check. Rooting is irreversible; adjacent checks matter.
- **#14159** proves UpdateParent accepts things replay then chokes on — an accept/replay asymmetry.
  Look for other places where validation at ingest is weaker than validation at use.
- **#14207** proves migration slot/epoch derivation was wrong once. Migration arithmetic is fertile.
- **#14208** (open) two ASN parsers — two parsers for one format is a divergence bug waiting to
  happen. Divergent parsing across nodes is a partition, i.e. safety/liveness, not cosmetic.

**Closed ≠ safe.** A closed issue means the code was recently patched, and the bounty explicitly
waives the one-week-on-master rule so fresh code is immediately in scope. Freshly-landed fixes are
among the highest-yield places to look: check each fix for incompleteness and for bugs introduced
by the fix itself.
