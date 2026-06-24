# sub-skill: refine-ui

Apply at most **1–3** high-value, low-risk improvements per night. Small reversible diffs only.

## Rubric (score each candidate; ship the highest)
- **Value**: does it help the user see usage/tokens/provenance/flow more clearly?
- **Safety**: reversible? scoped to one panel? no new heavy dependency?
- **Consistency**: matches the dark, professional theme (CSS variables in `index.html`)?
- **Evidence**: is it justified by a feed/best-practice learning or a real gap?

## Allowed change types
- Clarify/instrument an existing panel (labels, tooltips, legends, empty states).
- Add a derived metric or chart from data the API already returns.
- Improve information density / hierarchy / accessibility (contrast, focus states).
- Fix a bug found by validate-ui.

## Tournament step
For any non-trivial change, sketch 2–3 variants (e.g., bar vs heat-grid vs sparkline), pick the one
that scores best on the rubric, and note in the log why the others lost.

## Hard rules
- Keep `index.html` self-contained; only CDN libs already present (Chart.js, D3).
- Never use `localStorage` for app-critical state that the page needs on first paint.
- Do not remove existing features. Preserve all tabs, drill-downs, and the API contract.
- Touch `serve.py` only when the UI genuinely needs new/!changed data; keep endpoints backward-compatible.
