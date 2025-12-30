# Replay Service

The Replay service enables **controlled re-emission** of previously ingested events.

It is the **core investigation tool** of the Pipeline Investigation Kit.

Replay answers the question:

> “What would happen if these exact events were processed again?”

---

## Endpoint

```bash
POST /replay
```

---

## Request Payload

```json
{
  "entity_id": "user_123",
  "start_time": "2025-12-28T00:00:00Z",
  "end_time": "2025-12-29T00:00:00Z",
  "limit": 50,
  "include_duplicates": false
}
```

---

## Parameters

| Field                | Description                          |
| -------------------- | ------------------------------------ |
| `entity_id`          | Entity whose events will be replayed |
| `start_time`         | Start of replay window (ISO-8601)    |
| `end_time`           | End of replay window (ISO-8601)      |
| `limit`              | Maximum number of events to replay   |
| `include_duplicates` | Whether to include duplicate events  |

All parameters are required except `limit` (defaults to 500).

---

## What Replay Does

Replay performs **read-only investigation** followed by optional re-emission.

Step by step:

1. Query `EventsTable` by `entity_id`
2. Filter events by time window
3. Apply deduplication rules
4. Build replay messages
5. Send messages to SQS
6. Emit metrics

Replay **never modifies** stored data.

---

## Replay Filtering Rules

Replay messages are built using the following rules:

* events without `event_id` are skipped
* events without `s3_bucket` or `s3_key` are skipped
* when `include_duplicates=false`, each `event_id` is emitted only once
* events are emitted in query order
* replay stops when `limit` is reached

These rules are conservative by design.

---

## Replay Output

```json
{
  "entity_id": "user_123",
  "start_time": "2025-12-28T00:00:00Z",
  "end_time": "2025-12-29T00:00:00Z",
  "scanned": 12,
  "sent": 7
}
```

### Fields

| Field     | Meaning                        |
| --------- | ------------------------------ |
| `scanned` | Number of DynamoDB items read  |
| `sent`    | Number of SQS messages emitted |

A response with `sent = 0` is **valid and meaningful**.

---

## DRY_RUN Mode

When `DRY_RUN=true`:

* DynamoDB is queried
* filtering rules are applied
* **no SQS messages are sent**
* metrics are still emitted

This allows safe estimation of replay impact.

---

## Observability

### Metrics

* `ReplayRequestedCount`
* `ReplayMessageCount`

### Logs

Replay logs include:

* query parameters
* filtering decisions
* final counts

All logs are structured JSON.

---

## Common Use Cases

### Missing Aggregates

Replay a specific day or entity to verify:

* whether events exist
* how many would be processed

---

### Late Data

Replay a delayed window to:

* surface late arrivals
* observe aggregate changes

---

### Duplicate Storms

Replay with `include_duplicates=false` to:

* verify deduplication
* limit downstream impact

---

## Safety Guarantees

* Replay is explicit
* Replay is scoped
* Replay is reversible
* Replay is observable

Nothing happens automatically.

---

## What Replay Is NOT

* Not a backfill engine
* Not a migration tool
* Not a repair mechanism by itself

Replay provides **visibility**, not magic.

---

## Design Philosophy

Replay is intentionally:

* conservative
* predictable
* debuggable

If replay feels “slow” or “manual”, that is by design.
