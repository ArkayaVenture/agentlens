# sub-skill: enrich-brain

Turn the night's research into durable, traversable knowledge.

## 1. Distil
From the latest `knowledge/ai-feed/` digests and `knowledge/best-practices/`, extract items that
change how we should work or what the dashboard should show. Write concise, deduplicated notes back
into `knowledge/best-practices/*.md` (merge, don't duplicate).

## 2. Build the AI-feed relationship graph
Maintain `dashboard/feed-graph.json` so the AI Feed can render as a chronological, related graph:
```json
{
  "nodes": [{"id":"2026-06-23:anthropic:claude-tag","date":"YYYY-MM-DD","provider":"Anthropic",
             "title":"…","category":"feature","impact":"high","url":"…"}],
  "edges": [{"from":"…","to":"…","rel":"same-provider|same-topic|follows|supersedes","weight":1}]
}
```
Rules for edges:
- `follows` — chronological link between consecutive items of the same provider or topic.
- `same-topic` — share a topic tag (models, agents, MCP, safety, pricing…). Compute simple tag overlap.
- `supersedes` — a newer item updates/replaces an older one (e.g., version bumps, deprecations).
Keep ~200 most recent nodes; prune older edges first.

## 3. Cross-link to work
Where a feed item relates to the user's actual workflows (e.g., a new MCP/skill the user uses),
note that in the item's record so the brain graph can connect "news" → "our sessions".

## Output
List what was distilled, and confirm `feed-graph.json` is valid JSON with node/edge counts.
