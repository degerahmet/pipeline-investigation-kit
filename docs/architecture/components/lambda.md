# Lambda

There are three functions.

## IngestFunction

Responsibilities:

- validate minimal schema
- compute stable `event_id`
- dedupe gate (DynamoDB conditional put)
- write raw JSON to S3 (immutable key)
- write metadata index to EventsTable
- emit metrics (EMF)

## ReplayFunction

Responsibilities:

- query EventsTable by `entity_id` + time window
- build replay messages
- send to SQS
- emit metrics (requested vs sent)

## ProcessorFunction (optional)

Responsibilities:

- consume SQS messages
- fetch raw object from S3
- normalize minimal schema
- compute placeholder aggregate and store versioned outputs
- emit metrics (processed/errors)

## Operational notes

- keep handlers thin; push logic into `src/*/logic.py`
- prefer deterministic outputs for testability.
