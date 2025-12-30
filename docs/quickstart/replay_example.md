# Replay Example

Replay queries events by `entity_id` + time window and pushes them to SQS.

---

## 1) Replay for an entity + window

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

Expected response:

```json
{
  "entity_id":"user_123",
  "start_time":"...",
  "end_time":"...",
  "scanned": 1,
  "sent": 1
}
```

---

## 2) Confirm messages are in SQS

```bash
aws sqs get-queue-attributes \
  --queue-url "$REPLAY_QUEUE_URL" \
  --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible
```

Example:

```json
{
  "Attributes": {
    "ApproximateNumberOfMessages": "1",
    "ApproximateNumberOfMessagesNotVisible": "0"
  }
}
```

---

## Message format

Each SQS message points to the raw event in S3:

```json
{
  "event_id": "...",
  "entity_id": "...",
  "event_time": "2025-12-28T23:59:59Z",
  "s3_bucket": "...",
  "s3_key": "raw/source=.../event_id=....json"
}
```
