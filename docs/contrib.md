# Contributing to Pipeline Investigation Kit

First of all: **thank you for considering contributing** 🙌  
This project aims to stay **simple, practical, and production-shaped**.

We welcome contributions that improve:

- debuggability
- clarity
- reliability
- developer experience

---

## Guiding Principles

1. **Investigation-first**  
   This is not a full data pipeline. Changes should help explain failures.

2. **Minimalism over features**  
   Prefer small utilities over frameworks. Avoid heavy dependencies.

3. **Production-shaped, not over-engineered**  
   Realistic defaults without unnecessary complexity.

4. **Local-first DX**  
   `sam local` must work without AWS credentials.

---

## How to Contribute

### Fork & clone

```bash
git clone https://github.com/degerahmet/pipeline-investigation-kit.git
cd pipeline-investigation-kit
```

### Create a branch

```bash
git checkout -b feat/short-description
```

### Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### Run tests

```bash
pytest
```

---

## Code Style

- Python 3.11+
- Explicit over clever
- Small, testable functions

---

## Testing

- New logic requires tests
- Tests live in `tests/unit`
- No real AWS calls in tests

---

## Pull Requests

Explain *why* the change exists and mention trade-offs.

---

Thanks for contributing 💙
