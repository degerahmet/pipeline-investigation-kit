# Quickstart

## Deploy

```bash
sam build
sam deploy --guided
```

## Ingest example

```bash
curl -sS -X POST "$API_URL/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "source":"demo",
    "event_type":"heartbeat",
    "entity_id":"user_123",
    "event_time":"2025-12-28T23:59:59Z",
    "payload":{"steps":10}
  }'
```

## Replay example

```bash
curl -sS -X POST "$API_URL/replay" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id":"user_123",
    "start_time":"2025-12-28T00:00:00Z",
    "end_time":"2025-12-29T00:00:00Z",
    "limit":50,
    "include_duplicates":false
  }'
```
