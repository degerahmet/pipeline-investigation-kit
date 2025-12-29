import boto3
from botocore.exceptions import ClientError

ddb = boto3.resource("dynamodb")

def conditional_put(table_name: str, item: dict, condition_expression: str) -> bool:
    """
    Returns True if inserted, False if condition failed (duplicate).
    """
    table = ddb.Table(table_name)
    try:
        table.put_item(Item=item, ConditionExpression=condition_expression)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return False
        raise

def put(table_name: str, item: dict) -> None:
    ddb.Table(table_name).put_item(Item=item)
