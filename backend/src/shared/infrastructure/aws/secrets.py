import json
import os
from functools import lru_cache

import boto3
from botocore.config import Config


@lru_cache(maxsize=1)
def secretsmanager_client():
    return boto3.client(
        "secretsmanager",
        config=Config(retries={"max_attempts": 3}),
        region_name=os.environ.get("AWS_REGION", "ap-south-1")
    )


@lru_cache(maxsize=32)
def get_secret(secret_id: str) -> str:
    """Fetch a secret string from AWS Secrets Manager."""
    resp = secretsmanager_client().get_secret_value(SecretId=secret_id)
    return resp["SecretString"]
