# X-Ray

We enable X-Ray to trace requests across API Gateway → Lambda and AWS SDK calls.

## What it helps with

- "Why is this request slow?"
- "Which dependency call is failing?" (DynamoDB/S3/SQS)
- End-to-end visibility when debugging incidents

## Notes

- X-Ray is helpful during investigations but optional for minimal stacks.
- Keep sampling reasonable in production environments.
