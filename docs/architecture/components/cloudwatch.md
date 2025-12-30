# CloudWatch

We use CloudWatch for:

- structured logs
- custom metrics via EMF (Embedded Metric Format)

## Logs

Each Lambda writes JSON logs to:

- `/aws/lambda/<FunctionName>`

These logs support quick investigation in CloudWatch Logs Insights.

## Metrics (EMF)

Namespace: `PipelineInvestigationKit`

Examples emitted by the functions:

- Ingest: `IngestLagMs`, `DuplicateCount`, `IngestAcceptedCount`
- Replay: `ReplayRequestedCount`, `ReplayMessageCount`
- Processor: `ProcessorMessageCount`, `ProcessorErrorCount`

## Why EMF?

- No separate `PutMetricData` calls (cheaper/simpler).
- Metrics show up automatically from logs.
- Easy to build dashboards and alarms.

## Next steps (for teams)

- Create alarms on error counts and lag percentiles.
- Add a dashboard grouping ingest/replay/processor metrics.
