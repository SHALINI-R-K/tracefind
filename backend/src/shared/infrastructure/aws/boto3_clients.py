from __future__ import annotations

import os
from functools import lru_cache

import boto3
from botocore.config import Config

_BOTO_CONFIG = Config(
    retries={"max_attempts": 3, "mode": "standard"},
    connect_timeout=2,
    read_timeout=10,
)


@lru_cache(maxsize=1)
def dynamodb_resource():
    return boto3.resource("dynamodb", config=_BOTO_CONFIG, region_name=_region())


@lru_cache(maxsize=1)
def dynamodb_client():
    return boto3.client("dynamodb", config=_BOTO_CONFIG, region_name=_region())


@lru_cache(maxsize=1)
def ses_client():
    return boto3.client("ses", config=_BOTO_CONFIG, region_name=_region())


@lru_cache(maxsize=1)
def bedrock_runtime_client():
    return boto3.client("bedrock-runtime", config=_BOTO_CONFIG, region_name=_region())


@lru_cache(maxsize=1)
def ssm_client():
    return boto3.client("ssm", config=_BOTO_CONFIG, region_name=_region())


def _region() -> str:
    return os.environ.get("AWS_REGION", "us-east-1")
