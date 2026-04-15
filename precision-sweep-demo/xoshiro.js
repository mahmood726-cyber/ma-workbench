// xoshiro128** — must produce byte-identical sequence to precision_sweep/xoshiro.py
(function (root) {
  'use strict';
  const MASK = 0xFFFFFFFF;
  function rotl(x, k) {
    return ((x << k) | (x >>> (32 - k))) >>> 0;
  }
  function mul32(a, b) {
    const aHi = (a >>> 16);
    const aLo = a & 0xFFFF;
    const bHi = (b >>> 16);
    const bLo = b & 0xFFFF;
    return (((aHi * bLo + aLo * bHi) << 16) + aLo * bLo) >>> 0;
  }
  function Xoshiro128SS(seed) {
    let s = (seed >>> 0);
    const state = [];
    for (let i = 0; i < 4; i++) {
      s = (s + 0x9E3779B9) >>> 0;
      let z = s;
      z = mul32(z ^ (z >>> 16), 0x85EBCA6B);
      z = mul32(z ^ (z >>> 13), 0xC2B2AE35);
      z = (z ^ (z >>> 16)) >>> 0;
      state.push(z);
    }
    if (state.every(x => x === 0)) { state[0] = 1; }
    this.s = state;
  }
  Xoshiro128SS.prototype.nextUint32 = function () {
    const result = (mul32(rotl(mul32(this.s[1], 5), 7), 9)) >>> 0;
    const t = (this.s[1] << 9) >>> 0;
    this.s[2] ^= this.s[0];
    this.s[3] ^= this.s[1];
    this.s[1] ^= this.s[2];
    this.s[0] ^= this.s[3];
    this.s[2] ^= t;
    this.s[3] = rotl(this.s[3], 11);
    return result;
  };
  Xoshiro128SS.prototype.random = function () {
    return this.nextUint32() / 4294967296.0;
  };
  Xoshiro128SS.prototype.uniform = function (lo, hi) {
    return lo + (hi - lo) * this.random();
  };
  Xoshiro128SS.prototype.normal = function (mu, sigma) {
    let u1 = this.random();
    const u2 = this.random();
    if (u1 === 0) u1 = 1e-12;
    const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    return mu + sigma * z;
  };
  root.Xoshiro128SS = Xoshiro128SS;
})(typeof window !== 'undefined' ? window : globalThis);
