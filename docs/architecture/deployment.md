# Deployment Architecture (AWS SAM)

This kit deploys with **AWS SAM** into a single stack:

## Resources

### API Gateway

**REST API** with two endpoints:

- `POST /ingest` → Ingest Lambda
- `POST /replay` → Replay Lambda

### Storage

- **S3 Bucket**: Immutable raw event payloads
- **DynamoDB Tables**:
    - `EventsTable`: Metadata and index records
    - `DedupeTable`: Idempotency gate for duplicate detection
    - `AggregatesTable`: Versioned aggregate results *(optional, only when `EnableProcessor=true`)*

### Messaging

- **SQS Queue**: `ReplayQueue` for event reprocessing

### Compute

**Lambda Functions**:

- `IngestFunction`: Validates and stores incoming events
- `ReplayFunction`: Queries and replays historical events
- `ProcessorFunction`: Consumes and processes events from SQS *(optional)*

## Parameters

- `EnableProcessor` (bool)
  - `false`: no processor / no aggregates table / no event source mapping
  - `true`: creates Processor + AggregatesTable and wires SQS → Processor

## Environments

Each Lambda receives env vars for resource names/urls:

- `RAW_BUCKET`
- `EVENTS_TABLE`
- `DEDUPE_TABLE`
- `REPLAY_QUEUE_URL`
- `AGG_TABLE` (processor only)
- `LOG_LEVEL`

## IAM

Each Lambda has a dedicated role with least-privilege access:

- Ingest: PutObject to raw bucket, PutItem to tables, PutMetricData/logging
- Replay: Query EventsTable, SendMessage to SQS
- Processor: GetObject from raw bucket, PutItem to AggregatesTable

## Components in this stack

- API Gateway (REST)
- Lambda (Ingest, Replay, optional Processor)
- DynamoDB (EventsTable, DedupeTable, optional AggregatesTable)
- S3 (raw immutable storage)
- SQS (ReplayQueue)
- CloudWatch (logs + EMF metrics)
- IAM (least privilege roles)
- X-Ray (tracing)
