# IAM

Each Lambda has a dedicated IAM role with least-privilege policies.

## IngestFunction Role

Typically needs:

- `s3:PutObject` to raw bucket
- `dynamodb:PutItem` / `dynamodb:UpdateItem` (and `DescribeTable`) for Events/Dedupe tables
- CloudWatch Logs permissions (basic execution role)
- (optional) X-Ray write

## ReplayFunction Role

Typically needs:

- `dynamodb:Query` on EventsTable (+ index/*)
- `sqs:SendMessage` to ReplayQueue
- CloudWatch Logs permissions
- (optional) X-Ray write

## ProcessorFunction Role (optional)

Typically needs:

- `s3:GetObject` from raw bucket
- `dynamodb:PutItem` to AggregatesTable
- `sqs:ReceiveMessage/DeleteMessage` via event source mapping
- CloudWatch Logs permissions
- (optional) X-Ray write

## Guidance

- Avoid wildcard actions/resources unless unavoidable.
- Prefer table ARN + `/index/*` where needed.
- Treat these roles as the "security contract" for the repo.
