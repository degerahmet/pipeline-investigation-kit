# Developer Guide – Troubleshooting

This section documents **real failure modes you are likely to see**, how to diagnose them, and what *not* to do.

This project is intentionally transparent:
if something looks wrong, the system is probably telling you something important.

---

## Core Troubleshooting Principle

> **Never “fix” before you understand.**

Use:

* logs
* metrics
* raw data
* replay

Do **not** patch blindly.

---

## Ingest Issues

### ❗ Ingest returns `DUPLICATE` unexpectedly

**This is not an error.**

Likely causes:

* client retries
* network timeouts
* upstream replay

What to check:

* same `event_id`
* same payload hash
* dedupe table entries

✅ Expected behavior.

---

### ❗ Ingest accepts but no data appears downstream

Check:

1. S3 bucket → raw object exists?
2. EventsTable → metadata row exists?
3. Status field (`ACCEPTED` vs `DUPLICATE`)

If raw exists, ingest is working.

---

## Replay Issues

### ❗ Replay returns `sent = 0`

This is the **most common confusion point**.

Possible reasons:

* no events in time window
* all events filtered out
* `include_duplicates=false`
* missing `s3_bucket` or `s3_key`

What to do:

```bash
aws dynamodb scan --table-name EVENTS_TABLE
```

Inspect rows manually.

---

### ❗ Replay scans items but sends nothing

Check:

* `status` field
* missing S3 references
* limit reached early

Replay is conservative by design.

---

## Processor Issues

### ❗ Processor not consuming messages

Checklist:

* Is `EnableProcessor=true`?
* Does event source mapping exist?
* Is SQS empty?

```bash
aws lambda list-event-source-mappings
```

---

### ❗ Processor runs but aggregates are wrong

This is expected during investigation.

Check:

* multiple aggregate versions
* input hashes
* sample event IDs

Aggregates are **diagnostic outputs**, not truth.

---

### ❗ Processor errors but queue drains

This is dangerous.

Fix immediately:

```bash
sam deploy --parameter-overrides EnableProcessor=false
```

This stops consumption without losing messages.

---

## SQS Issues

### ❗ Messages disappear

Possible causes:

* processor enabled
* visibility timeout expired
* DLQ not configured (by design)

Always inspect before enabling processor.

---

### ❗ SQS stays empty after replay

Check:

* replay logs
* `sent` count
* IAM permissions (`sqs:SendMessage`)

---

## DynamoDB Issues

### ❗ Scan works but query doesn’t

Likely:

* wrong index
* wrong key condition
* wrong partition key

Remember:

* `PK = ENTITY#<id>`
* `SK = TS#<timestamp>#EID#<id>`

---

### ❗ Unexpected aggregate overwrites

Aggregates are **append-only** by design.

If you see overwrites:

* check table schema
* check sort key versioning
* verify code changes

---

## Logging & Metrics Issues

### ❗ No logs in CloudWatch

Check:

* correct log group name
* correct region
* IAM role includes `AWSLambdaBasicExecutionRole`

---

### ❗ Metrics missing

Ensure:

* EMF logs emitted
* namespace `PipelineInvestigationKit`
* correct dimensions

Metrics are written via logs.

---

## Local vs Cloud Confusion

### ❗ Works locally but not in AWS

Common causes:

* missing IAM permission
* missing env var
* wrong resource name

Compare:

```bash
sam local invoke
aws lambda invoke
```

Side-by-side.

---

## Golden Debugging Path

When confused, always do this in order:

1. Inspect raw S3 data
2. Inspect EventsTable rows
3. Replay with DRY_RUN
4. Inspect SQS messages
5. Enable processor briefly
6. Inspect aggregates

Never skip steps.

---

## What NOT to Do

❌ Delete raw data
❌ Rewrite aggregates
❌ Disable dedupe
❌ Replay without scoping
❌ Enable processor blindly

---

## When to Escalate

Escalate if:

* raw data missing
* ingest fails consistently
* IAM denies expected access

Otherwise, the system is likely behaving correctly.

---

## Developer Guide Complete ✅

You now have:

* Architecture
* Quickstart
* Deployment
* Configuration
* Usage
* Troubleshooting

This is a **complete, production-grade investigation toolkit**.
