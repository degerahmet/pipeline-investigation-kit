# Developer Guide – Usage

This section explains **how the system is meant to be used day-to-day**, especially during data pipeline incidents.

This is not a “happy path” guide.
It is an **investigation-first workflow**.

---

## Core Usage Philosophy

The Pipeline Investigation Kit is designed to answer questions like:

* Where did data break?
* When did it arrive late?
* Why did aggregates change?
* Can we replay safely?

**It is not a production pipeline.**
It is a **truth-preserving diagnostic layer**.

---

## Normal Flow (High Level)

1. **Ingest** receives events
2. **Raw data** is stored immutably in S3
3. **Metadata** is indexed in DynamoDB
4. **Replay** selectively re-emits events
5. **Processor** computes aggregates (optional)

Each step is independently observable.

---

## Ingest Usage

### When to Use Ingest

* collecting raw events
* capturing late/out-of-order data
* recording “bad” events instead of dropping them

### Example Ingest Call

```bash
curl -X POST "$API_URL/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "source":"demo",
    "event_type":"heartbeat",
    "entity_id":"user_123",
    "event_time":"2025-12-28T23:59:59Z",
    "payload":{"steps":10}
  }'
```

### Typical Responses

| Status      | Meaning               |
| ----------- | --------------------- |
| `ACCEPTED`  | First time event seen |
| `DUPLICATE` | Idempotent replay     |
| `REJECTED`  | Invalid payload       |

Duplicates are **expected** and **useful**.

---

## Replay Usage

Replay is the heart of investigations.

### When to Replay

* missing aggregates
* incorrect dashboards
* delayed syncs
* backfills

Replay never mutates data directly.

---

### Replay Example

```bash
curl -X POST "$API_URL/replay" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id":"user_123",
    "start_time":"2025-12-28T00:00:00Z",
    "end_time":"2025-12-29T00:00:00Z",
    "limit":50,
    "include_duplicates":false
  }'
```

### Replay Output

```json
{
  "entity_id": "user_123",
  "scanned": 1,
  "sent": 1
}
```

* `scanned` = DynamoDB items scanned
* `sent` = SQS messages emitted

If `sent = 0`, that’s a **signal**, not an error.

---

## Processor Usage

Processor is **optional** and **dangerous by design**.

### When to Enable Processor

Only after:

* ingest validated
* replay verified
* messages inspected

Processor consumes from SQS automatically.

---

### Processor Output

Processor writes:

* versioned aggregates
* input hashes
* sample event IDs

This allows full auditability.

---

## Aggregate Inspection

Query aggregates directly:

```bash
aws dynamodb scan \
  --table-name "$AGG_TABLE"
```

Look for:

* multiple versions per day
* changed input hashes
* unexpected recomputations

Aggregate churn is a **symptom**, not a bug.

---

## Typical Investigation Playbooks

### 🔍 Missing Day

1. Replay for that day
2. Inspect `sent` count
3. Enable processor
4. Compare aggregate versions

---

### 🐢 Late Data

1. Check ingest lag metrics
2. Query metadata by lag index
3. Replay late window
4. Observe aggregate change

---

### 🔁 Duplicate Storm

1. Ingest duplicates safely
2. Replay with `include_duplicates=false`
3. Confirm dedupe behavior
4. Validate downstream idempotency

---

## DRY_RUN Workflow (Strongly Recommended)

Before any real replay:

```bash
DRY_RUN=true
```

This lets you:

* measure blast radius
* estimate replay size
* validate filters

Only disable DRY_RUN when confident.

---

## Usage Anti-Patterns

### ❌ Treating Replay as “Fix Button”

Replay is not magic.
Bad inputs produce bad outputs.

---

### ❌ Blindly Enabling Processor

Processor should be:

* intentional
* temporary
* observable

---

### ❌ Deleting Raw Data

Raw data is your **ground truth**.
Never delete it during an investigation.

---

## Usage Checklist

Before closing an incident:

* [ ] Raw events verified
* [ ] Replay scoped correctly
* [ ] Processor behavior observed
* [ ] Aggregate version validated
* [ ] Root cause documented

---

## Next: Troubleshooting

Next we’ll cover:

* common failure modes
* misleading symptoms
* how to debug safely

👉 Continue with **Guide → Troubleshooting**
