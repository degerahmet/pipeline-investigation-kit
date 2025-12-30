# Architecture Overview

This project is an **investigation + observability kit** for data pipelines: it captures **immutable raw events**, indexes them for fast querying, measures **lag**, detects **duplicates**, and supports **replay** into a queue for downstream processing.

It is intentionally **production-shaped**, but **not** a full ETL/warehouse pipeline.

## Core Goals

- **Immutable raw storage**: keep the original event payloads as they arrived.
- **Idempotent ingestion**: stable `event_id`, dedupe gate, safe retries.
- **Fast investigation**: query by entity/time windows, find gaps/late arrivals, see which sources/types are problematic.
- **Replay**: push historical events back into a queue for reprocessing.
- **Traceability**: aggregate outputs store input hashes and sample event_ids.

## High-level flow

### 1. Event Ingestion

**Producer** → **Ingest API** (`POST /ingest`)

- Validates incoming event payload
- Computes stable `event_id` (for idempotency)
- Writes to three destinations:
    1. **S3**: Raw JSON with immutable object key
    2. **DynamoDB**: Metadata and index records for fast querying
    3. **CloudWatch**: Metrics and structured logs

### 2. Investigation & Replay

**Investigator** → **Replay API** (`POST /replay`)

- Queries **DynamoDB** for historical events (by entity, time range, etc.)
- Sends selected events to **SQS** queue for reprocessing

### 3. Event Processing (Optional)

**Processor Lambda** ← **SQS Queue**

1. Loads raw event from **S3**
2. Normalizes data to minimal schema
3. Computes placeholder aggregate
4. Stores versioned results with input hashes for auditability

## Key extension points

- **Schema**: extend allowed fields / validation in `src/shared/schema.py`
- **Partitioning**: change S3 key layout and DynamoDB PK/SK format in shared utilities
- **Replay output**: customize message payload for your downstream processors
- **Processor**: replace placeholder aggregates with domain logic; keep input hashes for auditability
