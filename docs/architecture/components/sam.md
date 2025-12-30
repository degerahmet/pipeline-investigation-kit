# AWS SAM

This repo uses AWS SAM to keep infra **small and reproducible**.

## Why SAM?

- one template (`template.yaml`)
- local iteration (`sam local start-api`)
- guided deploy (`sam deploy --guided`)
- parameterized optional processor (`EnableProcessor`)

## Where to look

- `template.yaml`: resources + IAM + env vars
- `.github/workflows/*` (if you add CI/CD later)
