// Golden-parity harness for the ACTUAL shipped browser JavaScript.
//
// The Python golden test (test_golden_parity.py) proves a Python
// re-implementation matches the committed references. This harness closes
// the remaining gap flagged in the audit: it extracts the real pooling
// engine (`wsum`, `tau2_PM`, `poolAll`) straight out of the shipped
// `workbench/index.html` and runs the 6 study-based golden datasets
// through it, diffing FE/RE/tau2/Q against golden/references/*.json.
//
// A numerical regression in the shipped pooling JS now fails CI.
//
// Usage:  node golden/js_parity.mjs            (from repo root)
// Exit 0 = all match; 1 = mismatch; 2 = harness/setup error.
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..");
const TOL = 1e-8;

const html = fs.readFileSync(path.join(ROOT, "workbench", "index.html"), "utf8");

// Slice the contiguous, DOM-free "Pooling and stats" block so we evaluate
// the real functions without executing the app's init/DOM code.
const startMarker = "// --- Pooling and stats";
const endMarker = "// Egger's test";
const si = html.indexOf(startMarker);
const ei = html.indexOf(endMarker, si);
if (si < 0 || ei < 0) {
  console.error("js_parity: pooling-block markers not found in workbench/index.html");
  process.exit(2);
}
const block = html.slice(si, ei);

let wsum, poolAll;
try {
  ({ wsum, poolAll } = new Function(block + "\n return { wsum, tau2_PM, poolAll };")());
} catch (e) {
  console.error("js_parity: failed to evaluate extracted JS:", e.message);
  process.exit(2);
}

const refsDir = path.join(ROOT, "golden", "references");
const dataDir = path.join(ROOT, "golden", "datasets");
const slugs = fs.readdirSync(refsDir).filter(f => f.endsWith(".json")).map(f => f.slice(0, -5));

const fails = [];
let n = 0;
for (const slug of slugs) {
  const ds = JSON.parse(fs.readFileSync(path.join(dataDir, slug + ".json"), "utf8"));
  if (!ds.bus_payload) continue; // MC datasets (e.g. G07) carry no study rows
  n++;
  const ref = JSON.parse(fs.readFileSync(path.join(refsDir, slug + ".json"), "utf8")).reference;
  const studies = ds.bus_payload.studies.map(s => ({ est: s.est, se: s.se, v: s.se * s.se }));
  const p = poolAll(studies);
  const fe = wsum(studies, 0);
  const feSe = Math.sqrt(1 / fe.sw);
  const checks = {
    "fe/estimate": [fe.mu, ref.fe.estimate],
    "fe/se": [feSe, ref.fe.se],
    "re_pm/estimate": [p.mu, ref.re_pm.estimate],
    "re_pm/se": [p.se, ref.re_pm.se],
    "re_pm/tau2": [p.tau2, ref.re_pm.tau2],
    "re_pm/qe": [p.Q, ref.re_pm.qe],
  };
  for (const [k, [a, b]] of Object.entries(checks)) {
    if (!(Math.abs(a - b) <= TOL)) {
      fails.push(`${slug} ${k}: js=${a} ref=${b} |d|=${Math.abs(a - b)}`);
    }
  }
}

if (n === 0) {
  console.error("js_parity: no study-based golden datasets found");
  process.exit(2);
}
if (fails.length) {
  console.error("js_parity FAILS:\n" + fails.join("\n"));
  process.exit(1);
}
console.log(`js_parity OK: shipped workbench pooling JS matches ${n} golden references to ${TOL}`);
process.exit(0);
