# SQS

SQS provides a simple replay buffer between investigation and processing.

## ReplayQueue

Replay Lambda sends one message per event:

```json
{
  "event_id": "...",
  "entity_id": "...",
  "event_time": "2025-12-28T23:59:59Z",
  "s3_bucket": "...",
  "s3_key": "raw/source=.../event_id=....json"
}
```

## Why SQS?

- Decouples replay from processing.
- Lets you scale the processor independently.
- Provides backpressure and retry behavior.

## Notes

- Processor is optional (EnableProcessor=true wires SQS → Processor Lambda).
- If processor is disabled, SQS still collects replay messages for external consumers.
