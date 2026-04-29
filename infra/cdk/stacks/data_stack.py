from __future__ import annotations

from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_dynamodb as ddb,
)
from constructs import Construct


class DataStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.items_table = ddb.Table(
            self,
            "ItemsTable",
            table_name="tracefind-items",
            partition_key=ddb.Attribute(name="id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            stream=ddb.StreamViewType.NEW_AND_OLD_IMAGES,
            time_to_live_attribute="ttl",
            removal_policy=RemovalPolicy.RETAIN,
            point_in_time_recovery=True,
        )
        self.items_table.add_global_secondary_index(
            index_name="GSI1",
            partition_key=ddb.Attribute(name="gsi1_pk", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="created_at", type=ddb.AttributeType.STRING),
        )
        self.items_table.add_global_secondary_index(
            index_name="GSI2",
            partition_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="created_at", type=ddb.AttributeType.STRING),
        )

        self.matches_table = ddb.Table(
            self,
            "MatchesTable",
            table_name="tracefind-matches",
            partition_key=ddb.Attribute(name="id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            stream=ddb.StreamViewType.NEW_AND_OLD_IMAGES,
            removal_policy=RemovalPolicy.RETAIN,
            point_in_time_recovery=True,
        )
        self.matches_table.add_global_secondary_index(
            index_name="GSI1",
            partition_key=ddb.Attribute(name="lost_item_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="created_at", type=ddb.AttributeType.STRING),
        )
        self.matches_table.add_global_secondary_index(
            index_name="GSI2",
            partition_key=ddb.Attribute(name="found_item_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="created_at", type=ddb.AttributeType.STRING),
        )

        self.claims_table = ddb.Table(
            self,
            "ClaimsTable",
            table_name="tracefind-claims",
            partition_key=ddb.Attribute(name="id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
            point_in_time_recovery=True,
        )
        self.claims_table.add_global_secondary_index(
            index_name="GSI1",
            partition_key=ddb.Attribute(name="claimant_user_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="created_at", type=ddb.AttributeType.STRING),
        )
        self.claims_table.add_global_secondary_index(
            index_name="GSI2",
            partition_key=ddb.Attribute(name="match_id", type=ddb.AttributeType.STRING),
        )

        self.notifications_table = ddb.Table(
            self,
            "NotificationsTable",
            table_name="tracefind-notifications",
            partition_key=ddb.Attribute(name="id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            time_to_live_attribute="ttl",
            removal_policy=RemovalPolicy.DESTROY,
        )
        self.notifications_table.add_global_secondary_index(
            index_name="GSI1",
            partition_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="created_at", type=ddb.AttributeType.STRING),
        )

        self.audit_table = ddb.Table(
            self,
            "AuditTable",
            table_name="tracefind-audit",
            partition_key=ddb.Attribute(name="id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
            point_in_time_recovery=True,
        )
        self.audit_table.add_global_secondary_index(
            index_name="GSI1",
            partition_key=ddb.Attribute(name="actor_user_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="created_at", type=ddb.AttributeType.STRING),
        )
