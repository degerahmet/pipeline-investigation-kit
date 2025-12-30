# Quickstart

Get the investigation kit running and validate the core flows:

1) Ingest events via HTTP  
2) Confirm dedupe behavior  
3) Replay events into SQS  
4) (Optional) Enable processor to compute aggregates

> This repo is an **investigation + observability toolkit**, not a full production pipeline.

---

## Prerequisites

- AWS account + credentials configured (`aws configure`)
- AWS SAM CLI installed
- Docker running (for `sam local`)
- Python 3.11+

---

## Deploy (dev)

From repo root:

```bash
sam build
sam deploy --guided
```

During `--guided`:

- **EnableProcessor**: set `false` first (you can enable later)
- Authentication: for initial testing you can choose `N` (public). For real use, secure it.

After deploy, you will get outputs like:

* `ApiUrl`
* `RawBucketName`
* `EventsTableName`
* `DedupeTableName`
* `ReplayQueueUrl`

Export them locally (replace values):

```bash
export API_URL="https://xxxxx.execute-api.us-east-1.amazonaws.com/Prod"
export REPLAY_QUEUE_URL="https://sqs.us-east-1.amazonaws.com/xxx/queue"
```

Next: follow the examples:

- [Ingest example](ingest_example.md)
- [Replay example](replay_example.md)
- [Processor example (optional)](processor_example.md)