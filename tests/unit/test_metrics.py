import json
from src.shared.metrics import emf

def test_emf_prints_valid_json(capsys):
    emf("TestNS", {"IngestCount": 1, "IngestLagMs": 123}, {"Function": "ingest", "Source": "demo"})
    out = capsys.readouterr().out.strip()
    payload = json.loads(out)

    assert payload["_aws"]["CloudWatchMetrics"][0]["Namespace"] == "TestNS"
    assert payload["Function"] == "ingest"
    assert payload["Source"] == "demo"
    assert payload["IngestCount"] == 1
    assert payload["IngestLagMs"] == 123
