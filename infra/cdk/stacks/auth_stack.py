from __future__ import annotations

from pathlib import Path

from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_cognito as cognito,
    aws_lambda as lambda_,
    aws_logs as logs,
)
from constructs import Construct


_SRC = (Path(__file__).resolve().parents[2].parent / "backend" / "src").as_posix()


class AuthStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.pre_signup_fn = lambda_.Function(
            self,
            "PreSignupFn",
            function_name="tracefind-pre-signup",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="contexts.identity_access.interfaces.cognito_triggers.pre_signup.lambda_handler",
            code=lambda_.Code.from_asset(_SRC),
            memory_size=256,
            timeout=Duration.seconds(5),
            log_retention=logs.RetentionDays.ONE_MONTH,
            tracing=lambda_.Tracing.ACTIVE,
            environment={"PYTHONPATH": "/var/task"},
        )

        self.user_pool = cognito.UserPool(
            self,
            "TraceFindUserPool",
            user_pool_name="tracefind-users",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(email=True),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True, mutable=False)
            ),
            password_policy=cognito.PasswordPolicy(
                min_length=10,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=False,
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            removal_policy=RemovalPolicy.RETAIN,
            lambda_triggers=cognito.UserPoolTriggers(
                pre_sign_up=self.pre_signup_fn,
            ),
        )

        cognito.CfnUserPoolGroup(
            self,
            "AdminGroup",
            user_pool_id=self.user_pool.user_pool_id,
            group_name="admin",
            description="TraceFind admin moderators",
        )

        self.user_pool_client = self.user_pool.add_client(
            "WebClient",
            generate_secret=False,
            auth_flows=cognito.AuthFlow(user_srp=True, user_password=False),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(authorization_code_grant=True),
                scopes=[cognito.OAuthScope.EMAIL, cognito.OAuthScope.OPENID],
            ),
        )
