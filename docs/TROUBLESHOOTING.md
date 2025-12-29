# Troubleshooting & FAQs

This page collects common developer issues and how to resolve them when working with the Pipeline Investigation Kit locally.

## 1. SAM local fails to start / missing credentials

- Problem: `sam local start-api` errors about credentials or cannot access AWS services.
- Fix: For pure local testing you can use `env/local.json` to configure endpoints and avoid live AWS calls. Ensure AWS credentials are in `~/.aws/credentials` when you intend to call real AWS. If a function attempts to contact DynamoDB/S3, run local emulators (e.g. LocalStack or DynamoDB Local) or mock those calls in tests.

## 2. `pytest` fails due to missing dependencies

- Problem: Tests fail with ImportError or missing packages.
- Fix: Activate the virtualenv and install dev requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt -r requirements-dev.txt
```

## 3. Tests failing that rely on AWS clients

- Problem: Tests that expect S3/DynamoDB access fail.
- Fix: Tests are written to avoid real AWS calls. Inspect `tests/unit/conftest.py` for fixtures that mock services. Run `pytest -q` to run unit tests that should be environment-independent.

## 4. Replay produces too many messages (fan-out)

- Problem: A replay request enqueues a large number of SQS messages.
- Fix: Use the `limit` parameter on replay requests to cap outputs. Also test with small time windows and `include_duplicates=false` when appropriate.

## 5. Duplicates in replays

- Problem: You see duplicate events during replay processing.
- Fix: Understand replay semantics: `include_duplicates=false` deduplicates by `event_id` within the single replay request. If upstream producers re-ingest the same event with different `event_id`s you will see multiple records.

## 6. Structured logs are hard to read in the terminal

- Problem: JSON logs are cumbersome to scan in raw form.
- Fix: Pipe logs through `jq` or use your editor/viewer to pretty-print. Example:

```bash
echo '{"level":"info","msg":"ok"}' | jq .
```

## 7. Local S3/DynamoDB emulation tips

- Use LocalStack or Dockerized DynamoDB Local for integration testing.
- Keep table/key names consistent with `env/local.json` to avoid surprises.

## 8. CI / Flaky tests

- Problem: Tests pass locally but fail in CI.
- Fix: Ensure CI uses the same Python version and installs `requirements-dev.txt`. Check for time-zone or locale-dependent assertions. Use deterministic timestamps in tests (see `tests/unit/test_timeutil.py`).

## 9. Permission errors when deploying

- Problem: `sam deploy` fails with IAM or S3 permission errors.
- Fix: Verify the AWS credentials used have: S3 PutObject for deployment artifacts, CloudFormation stack create/update, and IAM for roles if creating them. For restricted environments, prepare a deployment role with necessary permissions.

## 10. Still stuck?

- Open an issue with: steps to reproduce, relevant logs, the command you ran, and a minimal event payload if applicable. Include `pytest -q` output if the problem relates to tests.
