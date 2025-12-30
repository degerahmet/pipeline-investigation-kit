# Ingest API

The Ingest API is the **entry point** of the Pipeline Investigation Kit.

Its responsibility is intentionally narrow:

* accept events
* deduplicate them safely
* store raw data immutably
* record metadata for investigation

It **does not** transform, enrich, or aggregate data.

---

## Endpoint

```bash
POST /ingest
```

---

## Request Payload

```json
{
  "source": "demo",
  "event_type": "heartbeat",
  "entity_id": "user_123",
  "event_time": "2025-12-28T23:59:59Z",
  "payload": {
    "steps": 10
  }
}
```

---

## Required Fields

| Field        | Description                                     |
| ------------ | ----------------------------------------------- |
| `source`     | Origin system (service, app, vendor)            |
| `event_type` | Logical event type                              |
| `entity_id`  | Entity identifier (user, device, account, etc.) |
| `event_time` | When the event actually occurred (ISO-8601)     |
| `payload`    | Arbitrary JSON payload                          |

All fields are required.

---

## Event ID Strategy

A **stable `event_id`** is generated server-side using a deterministic hash:

```
hash(source + event_type + entity_id + event_time + payload)
```

This guarantees:

* idempotent ingestion
* safe client retries
* deterministic deduplication
* reproducible replay

Clients **do not** send `event_id`.

---

## Deduplication Behavior

Deduplication is based on `event_id`.

* First occurrence → `ACCEPTED`
* Subsequent occurrences → `DUPLICATE`

Duplicates are:

* expected
* recorded
* observable

They are **not errors**.

---

## Storage Model

### Raw Events (S3)

* Stored as immutable JSON objects
* Never overwritten or deleted by the system
* Partitioned by:

  * source
  * event_type
  * event_date
  * ingest_date
  * hour

Example key:

```bash
raw/source=demo/event_type=heartbeat/event_date=2025-12-28/ingest_date=2025-12-29/hour=23/event_id=....json
```

---

### Metadata (DynamoDB)

Each ingest writes a metadata record containing:

* event identifiers
* entity and time info
* ingest timestamp
* ingest lag
* status (`ACCEPTED` / `DUPLICATE`)
* S3 location
* payload hash

This table is optimized for investigation queries.

---

## Ingest Lag

The system computes:

```
ingest_lag_ms = ingest_time - event_time
```

This allows detection of:

* late arrivals
* backfills
* delayed syncs

Lag is indexed and queryable.

---

## Responses

### Accepted Event

```json
{
  "event_id": "...",
  "status": "ACCEPTED",
  "ingest_lag_ms": 72936580,
  "s3_key": "raw/..."
}
```

---

### Duplicate Event

```json
{
  "event_id": "...",
  "status": "DUPLICATE",
  "ingest_lag_ms": 72956085,
  "s3_key": "raw/..."
}
```

The same `event_id` is returned for duplicates.

---

## DRY_RUN Mode

When `DRY_RUN=true`:

* payload is validated
* `event_id` is generated
* no S3 writes
* no DynamoDB writes
* metrics are still emitted

This enables **safe testing in production**.

---

## Observability

### Metrics

* `IngestRequestCount`
* `DuplicateCount`
* `IngestLagMs`

### Logs

* structured JSON
* include event_id and entity_id
* safe for correlation

---

## Failure Handling

* Invalid payload → rejected
* Missing fields → rejected
* Internal errors → surfaced

No data is silently dropped.

---

## Design Guarantees

* Raw data is immutable
* Deduplication is deterministic
* Ingest is idempotent
* No side effects beyond storage

---

## When to Use Ingest

* capturing raw events
* recording late or out-of-order data
* preserving investigation context
* debugging upstream failures

If you are unsure whether to ingest something: **ingest it**.
