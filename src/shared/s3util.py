import json
import boto3
from typing import Any

s3 = boto3.client("s3")

def put_json_immutable(bucket: str, key: str, obj: Any) -> None:
    """
    Writes JSON to S3.
    'Immutable' means: the key should be unique (we use event_id in the key),
    so we never overwrite the same object in normal operation.
    """
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8"),
        ContentType="application/json",
        ServerSideEncryption="AES256",
    )

def get_json(bucket: str, key: str) -> Any:
    resp = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(resp["Body"].read().decode("utf-8"))
