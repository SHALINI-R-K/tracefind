#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk.stacks.auth_stack import AuthStack
from cdk.stacks.data_stack import DataStack
from cdk.stacks.api_stack import ApiStack

app = cdk.App()

env_name = app.node.try_get_context("env") or os.environ.get("ENV", "dev")
aws_env = cdk.Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1"),
)

auth = AuthStack(app, f"TraceFind-Auth-{env_name}", env=aws_env)
data = DataStack(app, f"TraceFind-Data-{env_name}", env=aws_env)
ses_from_email = os.environ.get("SES_FROM_EMAIL")
if not ses_from_email:
    raise RuntimeError(
        "SES_FROM_EMAIL is required for synth/deploy — must be a verified SES sender address."
    )

ApiStack(
    app,
    f"TraceFind-Api-{env_name}",
    env=aws_env,
    user_pool=auth.user_pool,
    user_pool_client=auth.user_pool_client,
    items_table=data.items_table,
    matches_table=data.matches_table,
    claims_table=data.claims_table,
    notifications_table=data.notifications_table,
    audit_table=data.audit_table,
    env_name=env_name,
    alarm_email=os.environ.get("ALARM_EMAIL"),
    ses_from_email=ses_from_email,
)

app.synth()
