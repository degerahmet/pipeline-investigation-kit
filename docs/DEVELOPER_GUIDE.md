# Developer Guide

This document helps contributors set up, run, test, and debug the Pipeline Investigation Kit locally.

## Quick summary

- Project root: repository contains three Lambda services under `src/`: `ingest`, `processor`, `replay`.
- Shared utilities live in `src/shared`.
- Infrastructure is described via AWS SAM (`template.yaml`).

## Prerequisites

- macOS / Linux / Windows WSL
- Python 3.11+ (match your system / virtualenv)
- pip
- AWS CLI configured if deploying to AWS
- AWS SAM CLI (for local invocation and deploy)

## Create a Python virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

If your system Python differs, adjust the `python` command accordingly.

## Local configuration

- `env/local.json` contains local environment overrides used for testing and development. Do not commit secrets.
- When running SAM locally you can pass environment via `--env-vars env/local.json`.

## Running the services locally (SAM)

Build and run the API locally:

```bash
sam build
sam local start-api --env-vars env/local.json
```

By default `start-api` serves the endpoints defined in `template.yaml`. Use `curl` or your browser to exercise endpoints:

```bash
curl -X POST http://127.0.0.1:3000/ingest -H "Content-Type: application/json" \
  -d @events/ingest-event.json

curl -X POST http://127.0.0.1:3000/replay -H "Content-Type: application/json" \
  -d @events/replay-event.json
```

Alternatively invoke a function directly with a test event:

```bash
sam local invoke IngestFunction --event events/ingest-event.json --env-vars env/local.json
```

Replace `IngestFunction` with the logical name in `template.yaml` if different.

## Running tests

Run the full unit test suite:

```bash
pytest -q
```

Run a single test file:

```bash
pytest tests/unit/test_ingest_logic.py -q
```

## Code layout and important files

- `src/ingest/app.py` — Lambda handler for ingest endpoint.
- `src/ingest/logic.py` — ingestion business logic.
- `src/processor/app.py` — processor Lambda handler.
- `src/processor/logic.py` — processor business logic.
- `src/replay/app.py` — replay Lambda handler.
- `src/replay/logic.py` — replay selection and SQS enqueue logic.
- `src/shared/` — helpers: `config.py`, `ddb.py`, `s3util.py`, `timeutil.py`, `validation.py`, `metrics.py`, `logging.py`.

Look at tests under `tests/unit/` for concrete examples of expected behavior and usage patterns.

## Linting and formatting

This repo includes developer requirements in `requirements-dev.txt`. Run your preferred linters/formatters before opening a PR.

Example (if `black` / `flake8` installed):

```bash
black src tests
flake8 src tests
```

## Debugging tips

- Check structured logs emitted by Lambdas (they are JSON). Logs usually show `event_id`, `entity_id`, and error details.
- Metrics names are defined in `src/shared/metrics.py` — useful for debugging ingest/replay counts.
- For replay issues, inspect DynamoDB table and S3 raw event objects referenced by replay messages.

## Running a local dry run of processor

Tests include a dry-run mode — see `tests/unit/test_processor_dry_run.py` for an example of how the processor is exercised without real SQS/S3.

## Deployment

Deploying safely to AWS and testing changes locally are important. This section explains common patterns for deployment with AWS SAM and options for local emulation.

### 1. Quick deploy (interactive)

```bash
sam build
sam deploy --guided
```

`--guided` will prompt for an S3 bucket to upload artifacts, a stack name, and whether you want to save those values to `samconfig.toml` for future non-interactive deploys.

### 2. Non-interactive deploy (CI-friendly)

Create or reuse an S3 bucket for artifacts and set CloudFormation parameter values, then:

```bash
sam build
sam deploy --no-confirm-changeset --stack-name my-pipeline-kit --s3-bucket my-sam-artifacts --capabilities CAPABILITY_IAM
```

In CI, prefer storing the stack name and bucket in environment variables. Ensure the IAM credentials used by CI have S3 PutObject, CloudFormation, and IAM permissions needed for role creation.

### 3. Local testing before deploy

- Use `sam local start-api --env-vars env/local.json` to exercise HTTP endpoints (`/ingest`, `/replay`) locally.
- For integration testing that needs S3/DynamoDB, use LocalStack or Dockerized DynamoDB Local and set `env/local.json` to point Lambdas at local endpoints.

Example using DynamoDB Local (Docker):

```bash
# start DynamoDB Local
docker run -d -p 8000:8000 --name dynamodb_local amazon/dynamodb-local
# update env/local.json to point to http://host.docker.internal:8000 or http://localhost:8000
sam local start-api --env-vars env/local.json
```

### 4. IAM & security notes

- Use least-privilege IAM policies for Lambda execution roles. If you let SAM create roles, review them after the first deploy.
- Do not store secrets in the repo; use Parameter Store or Secrets Manager and inject values via environment variables.

### 5. Common deployment troubleshooting

- "AccessDenied" on `sam deploy`: the credentials used lack S3/CloudFormation permissions. Use an account with deploy permissions or supply a deployment role.
- Long build times / package size issues: check large dependencies; consider using Lambda layers for heavy libraries.

### 6. Rollback and cleanup

To remove the stack and artifacts:

```bash
sam delete --stack-name my-pipeline-kit
```

Or remove via the CloudFormation console to inspect events and rollback reasons.

### 7. Verifying a deployment

- After `sam deploy`, use the outputs in the `samconfig.toml` or CloudFormation outputs to find the API Gateway endpoint.
- Hit the `ingest` and `replay` endpoints with sample payloads (see `events/`) and inspect CloudWatch logs for the corresponding Lambda to verify behavior.

### 8. CI/CD example (minimal)

In CI (GitHub Actions / other), typical steps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
sam build
sam package --s3-bucket $SAM_ARTIFACTS_BUCKET --output-template-file packaged.yaml
sam deploy --template-file packaged.yaml --stack-name $STACK_NAME --capabilities CAPABILITY_IAM --no-fail-on-empty-changeset
```

Record `SAM_ARTIFACTS_BUCKET` and `STACK_NAME` as CI secrets or environment variables.

## Contributing

Please follow the conventions in `CONTRIBUTING.md`. Open a small PR with a clear description and link to any issue. Include tests for behavioral changes.

## Frequently asked developer questions

- Q: Where are environment variables defined for Lambda locally?
  - A: Use `env/local.json` and pass it to SAM via `--env-vars`.
- Q: How to replay events locally?
  - A: Start API with `sam local start-api` and POST to `/replay` with `events/replay-event.json` as payload.

## Next steps for contributors

- Add tests for bugs or new features.
- Keep PRs small and focused.
- If adding new infra, update `template.yaml` and document required IAM permissions.

If something here is unclear, open an issue or a draft PR and I can help update these instructions.
