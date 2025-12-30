# Processor Service

The Processor service consumes replayed events and produces **derived aggregates**.

It is the **execution layer** of the Pipeline Investigation Kit.

Processor answers the question:

> “Given these events, what metrics should exist?”

---

## Role in the Pipeline

```
Replay API → SQS → Processor → AggregatesTable
```

Processor **never** talks to the API directly.
It only reacts to messages already validated and scoped by Replay.

---

## Input Source

Processor is triggered by an **SQS queue** populated by the Replay service.

Each message represents a **single immutable event reference**:

```json
{
  "event_id": "e123",
  "entity_id": "user_123",
  "event_time": "2025-12-28T23:59:59Z",
  "s3_bucket": "pipeline-raw-bucket",
  "s3_key": "raw/source=demo/..."
}
```

---

## Processing Flow

For each message:

1. Load raw event from S3
2. Validate payload structure
3. Apply aggregation logic
4. Write aggregate results to DynamoDB
5. Emit metrics

Failures are isolated per message.

---

## Aggregation Model

Processor writes results into **AggregatesTable**.

Each aggregate represents a **windowed metric**.

Example:

```json
{
  "PK": "ENTITY#user_123",
  "SK": "DAY#2025-12-28#VER#1767043865",
  "metric_name": "daily_event_count",
  "value": 1,
  "window_start": "2025-12-28T00:00:00Z",
  "window_end": "2025-12-28T23:59:59Z"
}
```

---

## Idempotency

Processor is **idempotent by design**.

* Aggregates are keyed by deterministic window identifiers
* Reprocessing the same event produces the same result
* Replay can safely be executed multiple times

---

## DRY_RUN Mode

When `DRY_RUN=true`:

* messages are read
* events are parsed
* metrics are computed
* **no DynamoDB writes occur**

Processor returns counts only.

This allows safe testing of aggregation logic.

---

## Metrics

Processor emits the following CloudWatch metrics:

* `ProcessorMessageCount`
* `ProcessorErrorCount`

These metrics are critical for validating replay outcomes.

---

## Error Handling

* malformed events are skipped
* missing S3 objects are logged
* aggregation failures increment error metrics
* the Lambda does **not crash the batch**

This ensures partial failures do not block investigations.

---

## Scaling Characteristics

* SQS controls concurrency
* Processor scales horizontally
* Backpressure is automatic

Replay volume directly controls processing pressure.

---

## What Processor Is NOT

* Not a stream processor
* Not real-time analytics
* Not a scheduler

Processor is intentionally **reactive and scoped**.

---

## Design Philosophy

Processor favors:

* determinism over speed
* observability over automation
* correctness over convenience

If results surprise you, the system is doing its job.

---

## Typical Workflow

1. Ingest raw events
2. Replay a scoped window
3. Observe processor metrics
4. Inspect aggregates
5. Iterate safely

Processor is an optional but powerful extension to the Pipeline Investigation Kit.
