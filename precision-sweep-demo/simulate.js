// Browser MC — must match precision_sweep/simulate.py bit-for-bit at 6 dp.
(function (root) {
  'use strict';

  function ivPoolLog(logHrs, ses) {
    let sw = 0, swy = 0;
    for (let i = 0; i < logHrs.length; i++) {
      const w = 1 / (ses[i] * ses[i]);
      sw += w;
      swy += w * logHrs[i];
    }
    return [swy / sw, Math.sqrt(1 / sw)];
  }

  function roundAtDp(v, dp) {
    const f = Math.pow(10, dp);
    return Math.round(v * f) / f;
  }

  function roundTrialAtDp(hr, logHr, seLogHr, dp) {
    const ciLow = Math.exp(logHr - 1.96 * seLogHr);
    const ciHigh = Math.exp(logHr + 1.96 * seLogHr);
    const hrR = roundAtDp(hr, dp);
    const loR = roundAtDp(ciLow, dp);
    const hiR = roundAtDp(ciHigh, dp);
    if (loR <= 0 || hiR <= 0 || loR >= hiR) {
      return [Math.log(Math.max(hrR, Math.pow(10, -dp))), Math.pow(10, -dp)];
    }
    const logHrR = hrR > 0 ? Math.log(hrR) : Math.log(Math.pow(10, -dp));
    const seR = (Math.log(hiR) - Math.log(loR)) / (2 * 1.96);
    return [logHrR, seR];
  }

  function runSimulation(inputs) {
    const rng = new root.Xoshiro128SS(inputs.seed);
    const logLo = Math.log(inputs.true_hr_range[0]);
    const logHi = Math.log(inputs.true_hr_range[1]);
    const seLo = inputs.se_range[0];
    const seHi = inputs.se_range[1];
    const deltas = {};
    inputs.dp_levels.forEach(dp => { deltas[dp] = []; });
    for (let i = 0; i < inputs.n_replications; i++) {
      const trueLogHr = rng.uniform(logLo, logHi);
      const se1 = rng.uniform(seLo, seHi);
      const se2 = rng.uniform(seLo, seHi);
      const logHr1 = trueLogHr + rng.normal(0, se1);
      const logHr2 = trueLogHr + rng.normal(0, se2);
      const hr1 = Math.exp(logHr1);
      const hr2 = Math.exp(logHr2);
      const truePoolLog = ivPoolLog([logHr1, logHr2], [se1, se2])[0];
      const truePoolHr = Math.exp(truePoolLog);
      for (const dp of inputs.dp_levels) {
        const [lh1r, s1r] = roundTrialAtDp(hr1, logHr1, se1, dp);
        const [lh2r, s2r] = roundTrialAtDp(hr2, logHr2, se2, dp);
        const plR = ivPoolLog([lh1r, lh2r], [s1r, s2r])[0];
        deltas[dp].push(Math.abs(Math.exp(plR) - truePoolHr));
      }
    }
    const per = {};
    for (const dp of inputs.dp_levels) {
      const v = deltas[dp].slice().sort((a, b) => a - b);
      const n = v.length;
      per[dp] = {
        median: v[Math.floor(n / 2)],
        p95: v[Math.floor(0.95 * n)],
        max: v[n - 1],
        frac_gt_0p001: v.filter(x => x > 0.001).length / n,
        frac_gt_0p005: v.filter(x => x > 0.005).length / n,
        frac_gt_0p01: v.filter(x => x > 0.01).length / n,
        frac_gt_0p02: v.filter(x => x > 0.02).length / n,
      };
    }
    return per;
  }

  root.precisionSweepSimulate = runSimulation;
})(typeof window !== 'undefined' ? window : globalThis);
