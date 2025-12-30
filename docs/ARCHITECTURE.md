# Architecture Overview

This document expands on the high-level architecture described in the README and explains the main components and data flow.

## High level

```
Producer → API Gateway → Ingest Lambda → S3 + DynamoDB
Replay API → Replay Lambda → SQS → Processor Lambda → DynamoDB
```

The system stores immutable raw events in S3 and keeps index/metadata in DynamoDB for quick retrieval by entity/time window. Replay reads the index and produces minimal messages that reference S3 objects for processing.

## Components

- Ingest service (`src/ingest`)

```
  - receives events via API Gateway
  - validates events and applies idempotency
  - writes raw event JSON to S3 and metadata to DynamoDB
  - emits metrics for ingest count, duplicates, and lag
```

- Replay service (`src/replay`)

```
  - accepts replay requests (entity + time window)
  - queries DynamoDB to find matching events
  - enqueues replay messages to SQS for downstream processors
```

- Processor service (`src/processor`)

```
  - consumes SQS messages produced by Replay
  - reads raw events from S3
  - performs domain-specific processing (aggregation, update DynamoDB)
  - emits success / error metrics
```

- Shared utilities (`src/shared`)

```
  - `ddb.py`: DynamoDB helper functions and table access patterns
  - `s3util.py`: S3 put/get helpers and path conventions
  - `validation.py`: event schema validation
  - `metrics.py`: metric name helpers
  - `logging.py`: structured logging wrapper
```

## Data model notes

- Raw events: stored in S3 as immutable JSON blobs. S3 keys include timestamp and `entity_id` to ease targeted retrieval.
- Index: DynamoDB contains a mapping of `entity_id` → list of event metadata (s3_key, event_time, event_id). This enables range queries by time window.
- Idempotency: ingest can accept an `idempotency_key` to de-duplicate upstream producer retries.

## Replay semantics

See README `Replay Semantics` for exact rules. Key points:

- Replay selects events by `entity_id` and time window.
- `include_duplicates=false` deduplicates by `event_id` within the replay request.
- Replay messages are intentionally minimal (S3 pointer + event_id) to avoid coupling.

## Observability

- Logs: structured JSON from Lambdas. Include `event_id`, `entity_id`, and correlation IDs where available.
- Metrics: Ingest and Processor emit metrics (see `src/shared/metrics.py`) for counts, errors, duplicate detection and ingest lag.

## Scaling and operational considerations

- DynamoDB access patterns: use efficient key design for range queries and avoid hot partitions.
- SQS fan-out: replay requests can create many messages; a `limit` parameter exists to restrict accidental broad replays.
- S3 lifecycle: raw events can be retained per team rules — consider lifecycle rules for longer retention.

## Security

- Least privilege IAM policies for Lambda functions is recommended.
- Avoid embedding secrets in code; use environment variables and AWS Secrets Manager or Parameter Store.