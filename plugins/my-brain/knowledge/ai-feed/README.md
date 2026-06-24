# AI Feed

Output of the scheduled research loops. Each run appends:
- `YYYY-MM-DD-daily.md` — daily release-notes digest (from `ai-release-radar`).
- `YYYY-MM-DD-weekly.md` — weekly deep dive (from `ai-deep-dive-weekly`).

Both loops also update `../../dashboard/feed.json`, which the dashboard reads.

**feed.json item schema**
```json
{
  "date": "YYYY-MM-DD",
  "provider": "Anthropic | OpenAI | Google | Meta | Mistral | xAI | Microsoft | AWS | ...",
  "category": "model | api | pricing | feature | research | safety | tooling",
  "impact": "high | medium | low",
  "title": "short headline",
  "summary": "1-3 sentences, verified",
  "url": "source link"
}
```
Each item must carry a source URL and be verified against the primary source (per the
adversarial step of the ultracode doctrine).
