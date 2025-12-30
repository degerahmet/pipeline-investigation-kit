# API Gateway

We expose a minimal REST API for investigation workflows.

## Endpoints

- `POST /ingest` → Ingest Lambda  
  Used by producers to submit raw events.

- `POST /replay` → Replay Lambda  
  Used by investigators to replay events for an entity + time window.

## Why API Gateway here?

- Standard HTTP interface teams can hit with curl/Postman.
- Easy to secure later (API keys, IAM auth, Cognito, Lambda authorizer).
- Works well for "deploy fast, investigate now" workflows.

## Current security posture

By default, the generated API may be public.
For open-source defaults, we keep it simple, but production teams should enable:
- auth (IAM/Cognito/authorizer)
- throttling / rate limits
- request validation + WAF if internet-facing
