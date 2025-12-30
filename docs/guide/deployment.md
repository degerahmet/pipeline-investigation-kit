# Developer Guide – Deployment

This section explains **how to deploy the Pipeline Investigation Kit safely**, and more importantly, **why the deployment is structured this way**.

The deployment strategy prioritizes:

* safety
* reversibility
* observability

---

## Deployment Model

The project is deployed using **AWS SAM (Serverless Application Model)**.

All infrastructure is defined in a single `template.yaml`, including:

* APIs
* Lambda functions
* DynamoDB tables
* S3 bucket
* SQS queue
* IAM roles
* event source mappings

There is **no manual AWS setup required**.

---

## Environments

The system is environment-aware by design.

Typical environments:

* `dev`
* `staging`
* `prod`

Each environment gets:

* isolated DynamoDB tables
* isolated S3 bucket
* isolated SQS queue
* isolated API Gateway stage

This prevents cross-environment data leakage.

---

## First-Time Deployment

Initial deployment should always be done with the processor **disabled**.

```bash
sam deploy --guided
```

When prompted for parameters:

```text
EnableProcessor = false
```

### Why?

Because:

* ingest and replay are safe without processing
* processor consumes messages automatically
* enabling it too early removes control

You want to **observe before acting**.

---

## Incremental Enablement Strategy

Deployment is intentionally split into phases.

### Phase 1 – Ingest Only

Enabled:

* Ingest API
* DynamoDB metadata tables
* S3 raw storage

Disabled:

* Processor
* Event source mapping

This allows you to verify:

* API works
* deduplication works
* raw data is stored correctly

---

### Phase 2 – Replay Enabled

Enabled:

* Replay API
* SQS queue

Still disabled:

* Processor

This allows:

* replay requests
* queue inspection
* message validation

You should manually inspect SQS messages at this stage.

---

### Phase 3 – Processor Enabled

Only after verification:

```bash
sam deploy --parameter-overrides EnableProcessor=true
```

This:

* creates the Processor Lambda
* attaches the SQS event source mapping
* begins automatic consumption

At this point the system is fully live.

---

## Safe Rollback Strategy

If something goes wrong:

### Disable Processor Immediately

```bash
sam deploy --parameter-overrides EnableProcessor=false
```

This:

* removes the event source mapping
* stops processing
* preserves queue messages

No data is lost.

---

## Deployment Is Idempotent

You can safely re-run deploy commands.

SAM + CloudFormation ensure:

* unchanged resources are not recreated
* data stores are preserved
* IAM roles are updated safely

---

## Zero-Downtime Behavior

The system is designed so that:

* APIs remain available during deploy
* SQS buffers messages
* processor restarts are safe

Temporary delays do **not** cause data loss.

---

## Common Deployment Mistakes

### ❌ Enabling Processor Too Early

Symptoms:

* messages disappear unexpectedly
* aggregates look incorrect
* difficult debugging

Fix:

* disable processor
* inspect replay output
* re-enable

---

### ❌ Forgetting Environment Isolation

Symptoms:

* replay returns unexpected data
* mixed test and prod data

Fix:

* verify stack name
* verify API URL
* verify table names

---

### ❌ Deploying Without Observability

Always verify:

* CloudWatch logs exist
* metrics are emitted
* DRY_RUN works

If you can’t observe it, don’t deploy it.

---

## Recommended Deployment Checklist

Before enabling processor:

* Ingest API responds correctly
* Duplicate events are detected
* Raw S3 objects exist
* Replay returns expected events
* SQS messages look correct
* DRY_RUN works end-to-end

Only then enable processing.

---

## Next: Configuration

Next we’ll cover:

* environment variables
* execution modes
* DRY_RUN behavior
* tuning knobs

👉 Continue with **Guide → Configuration**
