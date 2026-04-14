# HTML Apps Portfolio Improvements — Design

Date: 2026-04-14
Workspace: `C:\HTML apps`
Owner: mahmood789 / mahmood726-cyber

## Goal

Improve the `C:\HTML apps` portfolio in four bounded tracks, with a savepoint after
each track so work survives usage-limit interruption. Keep every track scoped; do
not expand into unrelated portfolio-wide changes outside this workspace.

## Non-Goals

- No changes to projects outside `C:\HTML apps\` (e.g., `C:\AdaptSim`, `C:\AlMizan`,
  `C:\NICECardiology`). The hub links to them but we will not edit them here.
- No new manuscript work, no F1000/PLOS submission changes.
- No dependency installs, `npm install` runs, or `node_modules` touches beyond what
  the existing apps already ship.
- No push / deploy / GitHub Pages enablement in this session.

## Scope (Four Tracks, Sequenced)

### Track 1 — Audit (read-only)

Produce `C:\HTML apps\AUDIT.md` containing:

- Inventory of every subdirectory with its declared entry file, actual entry file,
  and whether each matches.
- Registered hub entries (`hub/projects.js`) cross-checked against disk — list any
  path that does not resolve.
- Duplicate / backup artifact census (e.g., `Truthcert1` has 10+ `.backup-*.html`
  files — list them and recommend cleanup policy without deleting).
- Test suite status per app (pytest / selenium presence, not a run).
- Gap list — evidence-synthesis and productivity topics not yet covered.

No file edits outside `AUDIT.md`.

### Track 2 — Hub polish

Edit only `hub/projects.js`, `hub/app.js`, `hub/styles.css`, and `index.html`:

- Remove entries whose path does not exist on disk (record removed entries in the
  audit, not in hub copy).
- Add entries for apps that exist on disk but are not listed (e.g., `living-meta`,
  `nma-pro-v2`, `nma-dose-response-app`, `IPD-Meta-Pro`, `HTA`, `Pairwiseai`).
- Confirm the four hero counters compute from the project list (not hardcoded).
- No layout redesign. Same structure, corrected content.

### Track 3 — Repair one app

Pick the worst-flagged app from the audit. Do one bounded repair pass:

- Fix the most-broken entry point or failing smoke test.
- Do NOT add features, do NOT refactor.
- Cap: 3 failure-rerun cycles per issue per `workflow.md` Bounded Repair Loops.
- If cap is hit, log blocker to the app's `STUCK_FAILURES.md` and move on.

### Track 4 — New gap-filler app: PRISMA 2020 Flow Diagram Generator

New folder: `C:\HTML apps\prisma-flow\`.

- Single-file `index.html`, no build step, no external CDN at runtime.
- Inputs: record counts for each PRISMA 2020 node (identification → screening →
  eligibility → included), separate identification / screening / included paths.
- Output: rendered SVG flow diagram, downloadable as SVG and PNG.
- Persistence: `localStorage` key `prisma-flow-v1` (unique per app).
- Accessibility: labels, keyboard-reachable form, prefers-reduced-motion honored.
- Deterministic: same inputs → byte-identical SVG output.
- Minimal test: one Python test that confirms (a) `index.html` is parseable HTML,
  (b) it contains the required node labels, (c) div balance passes.
- Files: `index.html`, `tests/test_prisma_flow.py`, `README.md`.
- No F1000 / E156 manuscript package in this session.

## Architecture Notes

Each existing app is self-contained in its own folder with its own `index.html`
and test directory. The hub is the only cross-cutting component. This design
preserves that pattern — the new PRISMA app follows the same shape as
`evidence-board` / `focus-studio` / `kanban-lab`.

## Savepoints

After each track, commit the track's changes with a message of the form:

```
html-apps: <track> — <one-line summary>
```

If work is interrupted before a commit, write `PROGRESS.md` at the workspace root
with done / in-progress / next-step state and add it to `.gitignore`.

## Verification Gate (per track)

- Track 1: `AUDIT.md` exists, path-exists table populated, gap list non-empty.
- Track 2: Every entry in `hub/projects.js` resolves on disk; counters match.
- Track 3: Narrow failing target is green OR blocker is logged in
  `STUCK_FAILURES.md` with cap-reached reason.
- Track 4: `python -m pytest tests/test_prisma_flow.py` green; `index.html` opens
  in a browser without console errors.

## Out-of-Scope Reminders

- No secrets committed.
- No hardcoded `C:\Users\...` paths in shipped HTML/CSS/JS.
- No `{{placeholder}}` or `TBD` left in shipped files.
- No `git push` unless user explicitly requests at the end.
