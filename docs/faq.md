# Frequently Asked Questions

### 1. How to run the API locally?

Use AWS SAM CLI to build and start the API locally:

```bash
sam build
sam local start-api --env-vars env/local.json
```