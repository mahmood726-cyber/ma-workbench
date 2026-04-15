"""xoshiro128** PRNG — deterministic across Python and JS.

Reference: https://prng.di.unimi.it/xoshiro128starstar.c
32-bit state, period 2^128 - 1, passes PractRand to 32 TB.
"""
from __future__ import annotations


MASK = 0xFFFFFFFF


def _rotl(x: int, k: int) -> int:
    return ((x << k) | (x >> (32 - k))) & MASK


class Xoshiro128SS:
    """32-bit xoshiro128** generator. Seeds from a single integer via
    SplitMix32-style expansion to four 32-bit words."""

    def __init__(self, seed: int):
        if not isinstance(seed, int) or seed < 0:
            raise ValueError("seed must be non-negative int")
        # Expand a single int to 4x 32-bit state via SplitMix32
        s = seed & MASK
        self.s = []
        for _ in range(4):
            s = (s + 0x9E3779B9) & MASK
            z = s
            z = ((z ^ (z >> 16)) * 0x85EBCA6B) & MASK
            z = ((z ^ (z >> 13)) * 0xC2B2AE35) & MASK
            z = (z ^ (z >> 16)) & MASK
            self.s.append(z)
        # Guard against all-zero state (xoshiro forbids it)
        if all(x == 0 for x in self.s):
            self.s = [1, 0, 0, 0]

    def next_uint32(self) -> int:
        result = (_rotl((self.s[1] * 5) & MASK, 7) * 9) & MASK
        t = (self.s[1] << 9) & MASK
        self.s[2] ^= self.s[0]
        self.s[3] ^= self.s[1]
        self.s[1] ^= self.s[2]
        self.s[0] ^= self.s[3]
        self.s[2] ^= t
        self.s[3] = _rotl(self.s[3], 11)
        return result

    def random(self) -> float:
        """Return a float in [0, 1) with 24 bits of precision."""
        return self.next_uint32() / 4294967296.0

    def uniform(self, lo: float, hi: float) -> float:
        return lo + (hi - lo) * self.random()

    def normal(self, mu: float, sigma: float) -> float:
        """Box-Muller: two uniforms → one normal. Deterministic."""
        import math
        u1 = self.random()
        u2 = self.random()
        # Guard u1 > 0 to avoid log(0); PRNG output is [0,1) so u1 can be 0
        if u1 == 0.0:
            u1 = 1e-12
        z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        return mu + sigma * z
