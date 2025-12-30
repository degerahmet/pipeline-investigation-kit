# Ingest Example

This sends a raw event into the system. The ingest Lambda will:

- validate schema
- compute stable `event_id`
- write immutable raw JSON to S3
- write metadata/index row to DynamoDB
- emit ingest metrics (lag, accepted/duplicate)

---

## 1) Send an event

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

Expected response:

```json
{
  "event_id": "...",
  "status": "ACCEPTED",
  "ingest_lag_ms": 12345,
  "s3_key": "raw/source=.../event_id=....json"
}
```

---

## 2) Send the same event again (dedupe)

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

Expected response:

```json
{
  "event_id": "...",
  "status": "DUPLICATE",
  "ingest_lag_ms": 12345,
  "s3_key": "raw/source=.../event_id=....json"
}
```

---

## Notes

- `event_id` is stable for identical logical events.
- `status=DUPLICATE` means the event was already seen before.
- The raw event is stored immutably in S3 under a partition-friendly prefix.
