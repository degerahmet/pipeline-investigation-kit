# Processor Example (Optional)

The processor consumes replay messages from SQS, loads raw events from S3,
and writes a placeholder aggregate row into DynamoDB for traceability.

---

## Enable processor

Deploy with:

```bash
sam deploy --parameter-overrides EnableProcessor=true
```

This will add:

* Aggregates DynamoDB table
* SQS → Processor Lambda event source mapping
* Processor Lambda + IAM role

---

## Trigger a run

1. Ingest an event (see ingest example)
2. Replay it (see replay example)
3. Processor should consume from SQS automatically

Check SQS (should go back to 0):

```bash
aws sqs get-queue-attributes \
  --queue-url "$REPLAY_QUEUE_URL" \
  --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible
```

---

## Verify aggregates table writes

List aggregates:

```bash
aws dynamodb scan \
  --table-name "<YOUR_AGG_TABLE_NAME>" \
  --max-items 20
```

You should see fields like:

* `metric_name` (e.g., `daily_event_count`)
* `value`
* `inputs_hash`
* `sample_event_ids`
* `computed_at`

---

## Why this is useful

It proves an investigation loop:
> raw events → replay → processor → changing aggregate history.
