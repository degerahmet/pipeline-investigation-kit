# Pipeline Investigation Kit

A minimal, production-shaped **data pipeline investigation toolkit**.

This repository helps teams **quickly investigate pipeline issues** such as:

- delayed or out-of-order events
- missing days / windows
- duplicate events
- unexplained aggregate changes

It is **not** a full ETL pipeline.  
It is an **observability + replay + forensics kit** that you can deploy in ~30–60 minutes.

---

## What this solves

Most teams debugging data pipelines ask the same questions:

- Where is data delayed?
- Which source or event type fails most?
- Which days or windows are missing?
- Why did a daily score / metric change?
- Can we replay raw events for a specific entity and time range?

This kit gives you:

- immutable raw events (S3)
- idempotent ingestion
- structured logs + metrics
- replay by entity + time window
- aggregate versioning with input hashes

---

## Architecture (high level)

Producer → API Gateway → Ingest Lambda → S3 + DynamoDB  
Replay API → Replay Lambda → SQS → Processor Lambda → DynamoDB

---

## Event schema (minimal)

```json
{
  "source": "ios_app | partner_api | device_stream",
  "event_type": "heartbeat | purchase | score_update",
  "entity_id": "user_123 | device_9",
  "event_time": "2025-12-28T23:59:59Z",
  "payload": { "any": "json" },
  "idempotency_key": "optional-stable-producer-key"
}
```

---

## Quickstart (AWS SAM)

```bash
sam build
sam deploy --guided
```

### Ingest

```bash
curl -X POST https://<API_URL>/ingest \
  -H "Content-Type: application/json" \
  -d '{"source":"demo","event_type":"heartbeat","entity_id":"user_123","event_time":"2025-12-28T23:59:59Z","payload":{"steps":10}}'
```

### Replay

```bash
curl -X POST https://<API_URL>/replay \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"user_123","start_time":"2025-12-28T00:00:00Z","end_time":"2025-12-29T00:00:00Z"}'
```

---

## Observability

Metrics:

- IngestCount
- DuplicateCount
- IngestLagMs
- ReplayMessageCount
- ProcessorErrorCount

Logs are structured JSON.

---

## What this is NOT

- Not a full ETL pipeline
- Not a BI system
- Not a data quality framework

This is an **investigation & replay toolkit**.

---

## Roadmap

- Missing window detection
- Athena table definitions
- CloudWatch dashboard template

## Developer docs

- Developer guide: [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)
- Architecture overview: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Contributing

Contributions are welcome.

See [CONTRIBUTING.md](./CONTRIBUTING.md) for:

- design principles
- local development rules
- testing expectations

## Documentation

https://degerahmet.github.io/pipeline-investigation-kit/
