# DynamoDB

We use DynamoDB as the **investigation index** (not as the raw payload store).

## Tables

### EventsTable

Stores metadata per event:

- `PK = ENTITY#<entity_id>`
- `SK = TS#<event_time>#EID#<event_id>`
Used to query: “for this entity, show events between start/end”.

Also includes a GSI for “source/type/day” analysis:

- `GSI1PK = SRC#<source>#TYPE#<event_type>#DAY#<YYYY-MM-DD>`
- `GSI1SK = LAG#<lag_ms>#TS#<ingest_time>#EID#<event_id>`

### DedupeTable
Idempotency gate:

- `PK = EVENT#<event_id>`
A conditional put ensures the first occurrence wins.

### AggregatesTable (optional)
Versioned aggregates:
- `PK = ENTITY#<entity_id>`
- `SK = DAY#<YYYY-MM-DD>#VER#<unix_ts>`
Store:
- `inputs_hash`
- `input_count`
- `sample_event_ids`

## Common customizations

- Add a GSI for: “find missing windows per day”
- Add TTL on DedupeTable to limit storage (e.g., 30–90 days)