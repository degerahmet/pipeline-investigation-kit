import os
import json

def test_processor_dry_run_returns_counts(monkeypatch):
    monkeypatch.setenv("DRY_RUN", "true")
    event = {"Records": [{"body": json.dumps({"s3_bucket": "b", "s3_key": "k"})}]}
    from importlib import reload
    from src.processor import app as processor_app
    reload(processor_app)
    out = processor_app.handler(event, None)
