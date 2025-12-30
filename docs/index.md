# Pipeline Investigation Kit

**A lightweight, open-source toolkit for investigating data pipeline failures.**

Pipeline Investigation Kit helps teams **observe, diagnose, and replay data issues** such as:

* late or out-of-order events
* missing days or windows
* duplicate ingestion
* inconsistent aggregates
* unexplained metric changes

It is **not** a production data pipeline.
It is a **truth-preserving investigation layer** you can deploy in under an hour.

---

## Why This Exists

Modern data pipelines fail silently.

By the time a dashboard is wrong:

* raw data is gone
* retries are invisible
* aggregates have overwritten history

This project solves that by introducing **immutable capture + controlled replay**.

---

## What This Toolkit Is

* ✔ Immutable raw event storage
* ✔ Idempotent ingestion
* ✔ Fine-grained replay by entity & time window
* ✔ Safe, opt-in processing
* ✔ Full observability (logs + metrics)
* ✔ Designed for debugging, not throughput

---

## What This Toolkit Is NOT

* ✘ Not a streaming platform
* ✘ Not a full ETL system
* ✘ Not a replacement for your data warehouse
* ✘ Not a real-time analytics engine

It complements your pipeline — it does not replace it.

---

## High-Level Architecture

**Ingest → Store → Inspect → Replay → (Optionally) Process**:

* Events are ingested once
* Raw data is stored immutably in S3
* Metadata is indexed in DynamoDB
* Replay selectively re-emits events
* Processor computes versioned aggregates (optional)

Every step is independently observable and reversible.

---

## Typical Use Cases

* Debugging missing daily aggregates
* Investigating delayed syncs
* Replaying historical data safely
* Auditing aggregate changes
* Understanding duplicate storms

---

## Design Principles

* **Investigation first**
* **Immutability over mutation**
* **Observability over automation**
* **Safety over convenience**
* **Reversible by default**

If something looks “inefficient”, it is probably intentional.

---

## Quick Start

Deploy with processor disabled:

```bash
sam deploy --guided
```

Start ingesting events immediately.

Enable replay and processor only when needed.

👉 See **Quickstart** for a hands-on walkthrough.

---

## Documentation Structure

* **Quickstart** → get running fast
* **Architecture** → understand how it works
* **Guide** → operate and debug safely
* **Services** → API & component details
* **FAQ** → common questions and pitfalls

---

## Who This Is For

* Backend engineers
* Data engineers
* Platform teams
* On-call responders
* Anyone debugging “impossible” data bugs

If you’ve ever said *“the data just disappeared”*, this is for you.

---

## Open Source

* MIT License
* Easy to fork
* Minimal AWS footprint
* Designed to be extended

Contributions are welcome.

👉 See [CONTRIBUTING.md](contrib.md)

---

## Next Steps

* 📘 Read the **Quickstart**
* 🧠 Explore the **Architecture**
* 🛠 Deploy in a dev environment
* 🔍 Use it during your next incident

---

**Pipeline Investigation Kit**
*Observe first. Replay safely. Understand the truth.*
