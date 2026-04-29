from __future__ import annotations

import os

import boto3
import pytest
from moto import mock_aws


@pytest.fixture
def aws_credentials() -> None:
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def dynamo_tables(aws_credentials):
    with mock_aws():
        client = boto3.client("dynamodb", region_name="us-east-1")
        _create_items(client, "test-items")
        _create_matches(client, "test-matches")
        _create_claims(client, "test-claims")
        _create_notifications(client, "test-notifications")
        _create_audit(client, "test-audit")
        from src.shared.infrastructure.aws import boto3_clients
        boto3_clients.dynamodb_resource.cache_clear()
        boto3_clients.dynamodb_client.cache_clear()
        yield {
            "items": "test-items",
            "matches": "test-matches",
            "claims": "test-claims",
            "notifications": "test-notifications",
            "audit": "test-audit",
        }


def _create_items(client, name: str) -> None:
    client.create_table(
        TableName=name,
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "user_id", "AttributeType": "S"},
            {"AttributeName": "created_at", "AttributeType": "S"},
            {"AttributeName": "gsi1_pk", "AttributeType": "S"},
        ],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST",
        GlobalSecondaryIndexes=[
            {
                "IndexName": "GSI1",
                "KeySchema": [
                    {"AttributeName": "gsi1_pk", "KeyType": "HASH"},
                    {"AttributeName": "created_at", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "GSI2",
                "KeySchema": [
                    {"AttributeName": "user_id", "KeyType": "HASH"},
                    {"AttributeName": "created_at", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
    )


def _create_matches(client, name: str) -> None:
    client.create_table(
        TableName=name,
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "lost_item_id", "AttributeType": "S"},
            {"AttributeName": "found_item_id", "AttributeType": "S"},
            {"AttributeName": "created_at", "AttributeType": "S"},
        ],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST",
        GlobalSecondaryIndexes=[
            {
                "IndexName": "GSI1",
                "KeySchema": [
                    {"AttributeName": "lost_item_id", "KeyType": "HASH"},
                    {"AttributeName": "created_at", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "GSI2",
                "KeySchema": [
                    {"AttributeName": "found_item_id", "KeyType": "HASH"},
                    {"AttributeName": "created_at", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
    )


def _create_claims(client, name: str) -> None:
    client.create_table(
        TableName=name,
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "claimant_user_id", "AttributeType": "S"},
            {"AttributeName": "match_id", "AttributeType": "S"},
            {"AttributeName": "created_at", "AttributeType": "S"},
        ],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST",
        GlobalSecondaryIndexes=[
            {
                "IndexName": "GSI1",
                "KeySchema": [
                    {"AttributeName": "claimant_user_id", "KeyType": "HASH"},
                    {"AttributeName": "created_at", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "GSI2",
                "KeySchema": [{"AttributeName": "match_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
    )


def _create_notifications(client, name: str) -> None:
    client.create_table(
        TableName=name,
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "user_id", "AttributeType": "S"},
            {"AttributeName": "created_at", "AttributeType": "S"},
        ],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST",
        GlobalSecondaryIndexes=[
            {
                "IndexName": "GSI1",
                "KeySchema": [
                    {"AttributeName": "user_id", "KeyType": "HASH"},
                    {"AttributeName": "created_at", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
    )


def _create_audit(client, name: str) -> None:
    client.create_table(
        TableName=name,
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "actor_user_id", "AttributeType": "S"},
            {"AttributeName": "target_id", "AttributeType": "S"},
            {"AttributeName": "created_at", "AttributeType": "S"},
        ],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST",
        GlobalSecondaryIndexes=[
            {
                "IndexName": "GSI1",
                "KeySchema": [
                    {"AttributeName": "actor_user_id", "KeyType": "HASH"},
                    {"AttributeName": "created_at", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "GSI2",
                "KeySchema": [
                    {"AttributeName": "target_id", "KeyType": "HASH"},
                    {"AttributeName": "created_at", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
    )
