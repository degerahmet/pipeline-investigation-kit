# Architecture Diagram

## Diagrams

### Producer

```text
                +----------------------+
Producer(s) --->| API Gateway (REST)   |
                |  /ingest   /replay   |
                +----------+-----------+
                           |
                           v
                    +------+------+
                    | Ingest Lambda|
                    | (idempotent) |
                    +---+------+---+
                        |      |
                        |      |  put_item / query
                        |      v
                        |   +--+-------------------+
                        |   | DynamoDB (indexes)   |
                        |   | EventsTable          |
                        |   | DedupeTable          |
                        |   +----------------------+
                        |
                        |  put_object (immutable)
                        v
                +-------+--------+
                | S3 Raw Bucket  |
                | raw/...        |
                +----------------+
```

### Investigator

```text
                           +-------------------+
                           | Replay Lambda     |
Investigator --------------| query EventsTable |
    (POST /replay)         | send SQS messages |
                           +---------+---------+
                                     |
                                     v
                              +------+------+
                              |  SQS Queue  |
                              | ReplayQueue |
                              +------+------+
                                     |
                                     v
                           +---------+----------+
                           | Processor Lambda   |
                           | (optional)         |
                           | get_object from S3 |
                           | put_item aggregates|
                           +---------+---------+
                                     |
                                     v
                           +---------+---------+
                           | DynamoDB          |
                           | AggregatesTable   |
                           +-------------------+
```

### Processor Lambda Flow

```text
                              +--------------+
                              |  SQS Queue   |
                              | ReplayQueue  |
                              +------+-------+
                                     |
                                     | poll messages
                                     v
                           +---------+----------+
                           | Processor Lambda   |
                           |                    |
                           | 1. Parse SQS body  |
                           |    (s3_bucket,     |
                           |     s3_key)        |
                           +---------+----------+
                                     |
                                     | get_object
                                     v
                              +------+------+
                              | S3 Raw      |
                              | Bucket      |
                              +------+------+
                                     |
                                     | load raw JSON
                                     v
                           +---------+----------+
                           | 2. Group by        |
                           |    entity + day    |
                           |                    |
                           | 3. Build aggregate |
                           |    - daily count   |
                           |    - inputs hash   |
                           |    - sample IDs    |
                           +---------+----------+
                                     |
                                     | put_item
                                     v
                              +------+-------+
                              | DynamoDB     |
                              | Aggregates   |
                              | Table        |
                              +--------------+
                                     |
                                     | emit metrics
                                     v
                              +------+-------+
                              | CloudWatch   |
                              | Metrics/Logs |
                              +--------------+
```

## Why this layout?

- S3 is the source of truth for raw payloads (cheap, immutable, queryable later via Athena if desired).
- DynamoDB is the investigation index: fast lookups by entity/time window and by source/type/day.
- SQS decouples replay from processing and allows controlled reprocessing at scale.
- Lambda keeps deployment simple and portable across teams.
