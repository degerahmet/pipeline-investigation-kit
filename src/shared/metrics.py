import json
from datetime import datetime, timezone

def emf(namespace: str, metrics: dict, dimensions: dict):
    """
    CloudWatch Embedded Metric Format (EMF).
    When you emit EMF to Lambda logs, CloudWatch automatically creates metrics
    """
    ts = int(datetime.now(timezone.utc).timestamp() * 1000)
    dims = [list(dimensions.keys())] if dimensions else [[]]

    payload = {
        "_aws": {
            "Timestamp": ts,
            "CloudWatchMetrics": [{
                "Namespace": namespace,
                "Dimensions": dims,
                "Metrics": [{"Name": k, "Unit": "Count" if k.endswith("Count") else "Milliseconds"} for k in metrics.keys()]
            }]
        },
        **dimensions,
        **metrics
    }
    print(json.dumps(payload, separators=(",", ":")))
