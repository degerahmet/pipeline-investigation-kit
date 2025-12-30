# Pipeline Investigation Kit

A minimal **event pipeline investigation & replay toolkit** built on AWS.

This repository helps you **ingest, inspect, replay, and recompute events** safely when something goes wrong in your data pipeline.

It is designed for **debugging and recovery**, not for replacing your main ETL or streaming system.

---

## What this repo does

Pipeline Investigation Kit lets you:

* ingest events **idempotently**
* store raw events **immutably**
* replay events by **entity + time window**
* recompute aggregates safely
* debug pipeline issues without pausing production

Typical use cases:

* wrong or changed metrics
* missing or delayed events
* duplicate ingestion
* reprocessing historical data
* post-mortem analysis

---

## What this is NOT

* ❌ not a real-time analytics system
* ❌ not a full ETL framework
* ❌ not a BI or reporting tool

This is an **investigation, replay, and recovery kit**.

---

## High-level architecture

```
Producer
  → API Gateway
    → Ingest Lambda
      → S3 (immutable raw events)
      → DynamoDB (metadata & dedupe)

Replay API
  → Replay Lambda
    → SQS
      → Processor Lambda
        → DynamoDB (aggregates)
```

All components are serverless and managed via **AWS SAM**.

---

## Event model (minimal)

```json
{
  "source": "demo",
  "event_type": "heartbeat",
  "entity_id": "user_123",
  "event_time": "2025-12-28T23:59:59Z",
  "payload": { "any": "json" }
}
```

* events are immutable
* deduplication is enforced at ingest time
* duplicates are recorded, not dropped

---

## Quickstart (AWS)

### 1. Build & deploy

```bash
sam build
sam deploy --guided
```

This creates:

* API Gateway
* Lambdas (Ingest, Replay, Processor)
* S3 bucket
* DynamoDB tables
* SQS queue

---

### 2. Ingest an event

```bash
curl -X POST https://<API_URL>/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source":"demo",
    "event_type":"heartbeat",
    "entity_id":"user_123",
    "event_time":"2025-12-28T23:59:59Z",
    "payload":{"steps":10}
  }'
```

---

### 3. Replay events

```bash
curl -X POST https://<API_URL>/replay \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id":"user_123",
    "start_time":"2025-12-28T00:00:00Z",
    "end_time":"2025-12-29T00:00:00Z"
  }'
```

Replay sends matching events to SQS for reprocessing.

---

## Observability

The system emits structured logs and CloudWatch metrics:

* ingest counts & lag
* duplicate counts
* replay message counts
* processor success / errors

All operations are traceable and repeatable.

---

## Documentation

Full documentation is available here:

👉 **[https://degerahmet.github.io/pipeline-investigation-kit/](https://degerahmet.github.io/pipeline-investigation-kit/)**

Includes:

* architecture overview
* quickstart examples
* service-level docs
* developer guide
* troubleshooting

---

## Contributing

Contributions are welcome.

Please read:

* [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## License

MIT License.
Use freely. No warranty.
