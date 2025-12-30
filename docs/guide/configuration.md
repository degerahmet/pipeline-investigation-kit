# Developer Guide – Configuration

This section explains **all runtime configuration options**, how they affect behavior, and which ones you are expected to customize.

The system follows a strict rule:

> **Configuration controls behavior, not code.**

---

## Configuration Model

All configuration is done via **environment variables**.

These are injected by:

* AWS SAM
* CloudFormation
* `sam local invoke --env-vars`

There are **no hard-coded environment-specific values** in the code.

---

## Required Environment Variables

These are injected automatically by the SAM template.

You should **never manually set them** in production.

### Storage & State

| Variable           | Purpose                            |
| ------------------ | ---------------------------------- |
| `RAW_BUCKET`       | S3 bucket for immutable raw events |
| `EVENTS_TABLE`     | DynamoDB table for event metadata  |
| `DEDUPE_TABLE`     | DynamoDB table for idempotency     |
| `AGG_TABLE`        | DynamoDB table for aggregates      |
| `REPLAY_QUEUE_URL` | SQS queue for replay               |

---

## Execution Mode Flags

### `DRY_RUN`

```text
DRY_RUN=true | false
```

**Most important flag in the system.**

Controls whether the system:

* writes data
* sends messages
* mutates state

#### Behavior

| Component | DRY_RUN=true   | DRY_RUN=false        |
| --------- | -------------- | -------------------- |
| Ingest    | validates only | writes S3 + DynamoDB |
| Replay    | scans only     | sends SQS messages   |
| Processor | counts only    | writes aggregates    |

#### Why DRY_RUN exists

* safe local testing
* safe production investigation
* zero-risk replay analysis

**Default:** `false`

---

### `LOG_LEVEL`

```text
LOG_LEVEL=INFO | DEBUG
```

Controls log verbosity.

* `INFO` → normal operation
* `DEBUG` → investigations only

Avoid `DEBUG` in production for cost reasons.

---

## Feature Toggles

### `EnableProcessor` (SAM Parameter)

This is a **deployment-time toggle**, not a runtime env var.

```bash
sam deploy --parameter-overrides EnableProcessor=true
```

Controls:

* creation of Processor Lambda
* creation of SQS event source mapping

This is the **safest kill switch** in the system.

---

## Replay Configuration

Replay behavior is controlled per-request.

### Replay Request Fields

| Field                | Description               |
| -------------------- | ------------------------- |
| `entity_id`          | Entity to replay          |
| `start_time`         | ISO-8601 start            |
| `end_time`           | ISO-8601 end              |
| `limit`              | Max messages              |
| `include_duplicates` | Include duplicates or not |

Replay never mutates data by itself.

---

## Aggregate Versioning

Aggregates are versioned automatically.

Each aggregate row includes:

* `inputs_hash`
* `computed_at`
* `VER#<timestamp>` in sort key

This allows:

* reprocessing
* comparison
* rollback
* auditability

No configuration needed.

---

## IAM Configuration

IAM permissions are **least-privilege by default**.

Each Lambda has:

* its own role
* scoped access
* no wildcard writes

You should **not extend IAM** unless adding new components.

---

## Local Configuration

For local testing:

```bash
sam local invoke IngestFunction \
  --env-vars env/local.json
```

Example `env/local.json`:

```json
{
  "IngestFunction": {
    "DRY_RUN": "true",
    "LOG_LEVEL": "DEBUG"
  }
}
```

Never commit real secrets.

---

## Configuration Anti-Patterns

### ❌ Hardcoding Resource Names

Breaks:

* environments
* deployments
* portability

---

### ❌ Using Code Flags Instead of Env Vars

Configuration must be:

* observable
* changeable
* reversible

---

### ❌ Running Without DRY_RUN First

Always validate behavior before mutating state.

---

## Configuration Checklist

Before production use:

* [ ] DRY_RUN tested
* [ ] Processor disabled initially
* [ ] LOG_LEVEL set correctly
* [ ] Replay tested
* [ ] IAM untouched

---

## Next: Usage

Next we’ll cover:

* normal operation
* investigation workflows
* replay patterns
* real-world examples

👉 Continue with **Guide → Usage**
