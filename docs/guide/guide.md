# Developer Guide – Overview

This guide explains **how to work with the Pipeline Investigation Kit as a developer**.

It assumes:

* you can read Python
* you are comfortable with AWS concepts
* you want to *understand the system*, not just deploy it

If you are only looking for a quick demo, see **Quickstart**.

---

## What This Project Is

Pipeline Investigation Kit is a **debug-first, replayable data ingestion pipeline** built on AWS serverless primitives.

It is designed to answer questions like:

* *What exactly happened to this event?*
* *Was it ingested?*
* *Was it deduplicated?*
* *Was it processed?*
* *Can we replay it safely?*

The system favors **observability and determinism** over raw throughput.

---

## What This Project Is NOT

This project is **not**:

* a real-time streaming system
* a generic ETL framework
* a batch analytics engine
* a low-latency event processor

Those trade-offs are intentional.

---

## Core Design Goals

### 1. Every Event Is Explainable

For any event, you should be able to reconstruct:

* when it arrived
* how late it was
* where it was stored
* whether it was deduplicated
* whether it was processed
* what output it produced

If an event cannot be explained, the system has failed.

---

### 2. Replay Is a First-Class Feature

Replay is not an afterthought.

The pipeline is explicitly designed so that:

* raw data is immutable
* metadata is queryable
* processing is repeatable

Replay is **safe by default**.

---

### 3. Idempotency Everywhere

All writes are designed to tolerate retries:

* ingest deduplication is explicit
* replay can re-enqueue safely
* processor logic tolerates duplicates
* aggregation is deterministic

You should never fear re-running a step.

---

### 4. DRY_RUN Is Production-Grade

`DRY_RUN=true` means:

* full logic execution
* no external side effects
* metrics are still emitted

This allows:

* local debugging
* production safety checks
* incident simulation

---

## High-Level Flow

At a high level, the system works like this:

1. **Ingest**

   * receives an event via HTTP
   * computes event identity
   * stores raw payload immutably
   * writes metadata
   * performs deduplication

2. **Replay**

   * queries historical events
   * applies filtering rules
   * enqueues replay messages

3. **Processor**

   * consumes replay messages
   * reads raw data from storage
   * computes aggregates
   * writes deterministic outputs

Each stage is isolated and independently testable.

---

## Mental Model for Developers

When working on this project, always ask:

* *Is this operation safe to retry?*
* *Can I explain this behavior later?*
* *Does this reduce or increase observability?*
* *Would DRY_RUN behave sensibly here?*

If the answer is unclear, stop and rethink.

---

## How the Guide Is Organized

This guide is split into focused sections:

* **Deployment**
  How the system is deployed and toggled safely.

* **Configuration**
  Environment variables, flags, and execution modes.

* **Usage**
  How to interact with the APIs and queues.

* **Troubleshooting**
  How to debug real production issues.

Each section assumes you’ve read this overview.

---

## Who This Guide Is For

This guide is written for:

* backend engineers
* platform engineers
* data engineers debugging pipelines
* anyone who has ever asked
  *“Why did this event disappear?”*

---

## Next: Deployment

Next, we’ll cover **Deployment**, including:

* environment strategy
* enabling / disabling processor safely
* rollout patterns
* common deployment mistakes

👉 Continue with **Guide → Deployment**
