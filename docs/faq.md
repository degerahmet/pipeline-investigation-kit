# Frequently Asked Questions

### 1. How to run the API locally?

Use AWS SAM CLI to build and start the API locally:

```bash
sam build
sam local start-api --env-vars env/local.json
```

### 2. How to enable the processor after deployment?

Update the CloudFormation stack with `EnableProcessor` set to `true`:

```bash
sam deploy --parameter-overrides EnableProcessor=true
```

### 3. How to customize the event schema?

Modify the event schema in the ingestion Lambda function code (`ingest/app.py`) and ensure downstream components are compatible.

### 4. How to monitor metrics and logs?

Use Amazon CloudWatch to monitor logs and metrics emitted by the Lambda functions. Look for custom metrics like `IngestCount` and `DuplicateCount`.

### 5. How to handle duplicate events?

The ingestion Lambda uses an idempotency key to detect duplicates. Ensure that your events include a stable `idempotency_key` field.

### 6. How to replay events for a specific entity and time window?

Use the replay API endpoint with the desired `entity_id`, `start_time`, and `end_time` parameters to fetch and enqueue events for processing.

### 7. How to test the entire flow end-to-end?

Follow the quickstart guide to deploy the stack, ingest events, verify deduplication, replay events, and optionally enable processing.

### 8. How to contribute to the project?

See the [CONTRIBUTING.md](contrib.md) file for guidelines on how to contribute to the project.