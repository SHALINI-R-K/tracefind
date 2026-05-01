from __future__ import annotations

from pathlib import Path

from aws_cdk import (
    Duration,
    Stack,
    aws_apigateway as apigw_v1,
    aws_apigatewayv2 as apigw,
    aws_apigatewayv2_authorizers as authz,
    aws_apigatewayv2_integrations as integ,
    aws_cloudwatch as cw,
    aws_cloudwatch_actions as cw_actions,
    aws_dynamodb as ddb,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_lambda_event_sources as les,
    aws_logs as logs,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subs,
    aws_secretsmanager as sm,
)
from constructs import Construct


_SRC = (Path(__file__).resolve().parents[2].parent / "backend" / "src").as_posix()


class ApiStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        user_pool,
        user_pool_client,
        items_table: ddb.Table,
        matches_table: ddb.Table,
        claims_table: ddb.Table,
        notifications_table: ddb.Table,
        audit_table: ddb.Table,
        env_name: str,
        ses_from_email: str,
        alarm_email: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self._env_name = env_name

        groq_secret_name = "tracefind/groq-api-key"

        common_env = {
            "ITEMS_TABLE": items_table.table_name,
            "MATCHES_TABLE": matches_table.table_name,
            "CLAIMS_TABLE": claims_table.table_name,
            "NOTIFICATIONS_TABLE": notifications_table.table_name,
            "AUDIT_TABLE": audit_table.table_name,
            "MATCH_THRESHOLD": "0.70",
            "EMBEDDING_MODEL_VERSION": "groq-vision+titan-text-v2",
            "COGNITO_USER_POOL_ID": user_pool.user_pool_id,
            "ENV": env_name,
            "PYTHONPATH": "/var/task",
            "GROQ_SECRET_NAME": groq_secret_name,
            "GROQ_MODEL": "meta-llama/llama-4-scout-17b-16e-instruct",
            "GROQ_TIMEOUT_SECONDS": "5",
            "SES_FROM_EMAIL": ses_from_email,
        }

        def fn(name: str, handler: str, *, memory: int = 256, timeout: int = 5) -> lambda_.Function:
            return lambda_.Function(
                self,
                name,
                function_name=f"tracefind-{name.lower()}-{env_name}",
                runtime=lambda_.Runtime.PYTHON_3_12,
                handler=handler,
                code=lambda_.Code.from_asset(_SRC),
                memory_size=memory,
                timeout=Duration.seconds(timeout),
                environment=common_env,
                log_retention=logs.RetentionDays.ONE_MONTH,
                tracing=lambda_.Tracing.ACTIVE,
            )

        create_item = fn(
            "CreateItem",
            "contexts.reporting.interfaces.http.create_item_handler.lambda_handler",
            memory=1024,
            timeout=15,
        )
        get_items = fn(
            "GetItems",
            "contexts.reporting.interfaces.http.get_items_handler.lambda_handler",
        )
        match_items = fn(
            "MatchItems",
            "contexts.matching.interfaces.events.on_item_reported.lambda_handler",
            memory=1024,
            timeout=15,
        )
        get_matches = fn(
            "GetMatches",
            "contexts.matching.interfaces.http.get_matches_handler.lambda_handler",
        )
        claim_item = fn(
            "ClaimItem",
            "contexts.claims.interfaces.http.claim_item_handler.lambda_handler",
        )
        notify_users = fn(
            "NotifyUsers",
            "contexts.notification.interfaces.events.on_match_found.lambda_handler",
            timeout=10,
        )
        list_notifications = fn(
            "ListNotifications",
            "contexts.notification.interfaces.http.notifications_handler.list_handler",
        )
        mark_notification_read = fn(
            "MarkNotificationRead",
            "contexts.notification.interfaces.http.notifications_handler.mark_read_handler",
        )
        admin_list_reports = fn(
            "AdminListReports",
            "contexts.admin.interfaces.http.admin_handler.list_reports_handler",
        )
        admin_archive = fn(
            "AdminArchive",
            "contexts.admin.interfaces.http.admin_handler.archive_item_handler",
        )
        admin_override = fn(
            "AdminOverrideMatch",
            "contexts.admin.interfaces.http.admin_handler.override_match_handler",
        )
        admin_reject = fn(
            "AdminRejectMatch",
            "contexts.admin.interfaces.http.admin_handler.reject_match_handler",
        )
        admin_audit = fn(
            "AdminAuditQuery",
            "contexts.admin.interfaces.http.admin_handler.audit_query_handler",
        )
        admin_reembed = fn(
            "AdminReembed",
            "contexts.reporting.interfaces.http.reembed_handler.lambda_handler",
            memory=1024,
            timeout=15,
        )

        items_table.grant_read_write_data(create_item)
        items_table.grant_read_data(get_items)
        items_table.grant_read_data(match_items)
        matches_table.grant_read_write_data(match_items)
        items_table.grant_read_data(get_matches)
        matches_table.grant_read_data(get_matches)
        items_table.grant_read_write_data(claim_item)
        matches_table.grant_read_write_data(claim_item)
        claims_table.grant_read_write_data(claim_item)
        notifications_table.grant_read_write_data(notify_users)
        items_table.grant_read_data(notify_users)
        notifications_table.grant_read_write_data(list_notifications)
        notifications_table.grant_read_write_data(mark_notification_read)
        items_table.grant_read_data(admin_list_reports)
        items_table.grant_read_write_data(admin_archive)
        audit_table.grant_read_write_data(admin_archive)
        items_table.grant_read_data(admin_override)
        matches_table.grant_read_write_data(admin_override)
        audit_table.grant_read_write_data(admin_override)
        matches_table.grant_read_write_data(admin_reject)
        audit_table.grant_read_write_data(admin_reject)
        audit_table.grant_read_data(admin_audit)
        items_table.grant_read_write_data(admin_reembed)

        match_items.add_event_source(
            les.DynamoEventSource(
                items_table,
                starting_position=lambda_.StartingPosition.LATEST,
                batch_size=10,
                bisect_batch_on_error=True,
                retry_attempts=3,
                report_batch_item_failures=True,
            )
        )
        notify_users.add_event_source(
            les.DynamoEventSource(
                matches_table,
                starting_position=lambda_.StartingPosition.LATEST,
                batch_size=10,
                bisect_batch_on_error=True,
                retry_attempts=3,
                report_batch_item_failures=True,
            )
        )

        notify_users.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ses:SendEmail", "ses:SendRawEmail"],
                resources=["*"],
            )
        )
        notify_users.add_to_role_policy(
            iam.PolicyStatement(
                actions=["cognito-idp:AdminGetUser"],
                resources=[user_pool.user_pool_arn],
            )
        )
        for f in (create_item, admin_reembed):
            f.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["bedrock:InvokeModel"],
                    resources=[
                        f"arn:aws:bedrock:{self.region}::foundation-model/amazon.titan-embed-text-v2:0",
                    ],
                )
            )

        groq_secret = sm.Secret.from_secret_name_v2(self, "GroqSecret", groq_secret_name)
        groq_secret.grant_read(create_item)
        groq_secret.grant_read(admin_reembed)

        if env_name == "prod":
            create_item_alias = lambda_.Alias(
                self,
                "CreateItemLiveAlias",
                alias_name="live",
                version=create_item.current_version,
            )
            create_item_alias.add_auto_scaling(
                min_capacity=1,
                max_capacity=10,
            ).scale_on_utilization(utilization_target=0.7)

        authorizer = authz.HttpJwtAuthorizer(
            "JwtAuthorizer",
            jwt_issuer=f"https://cognito-idp.{self.region}.amazonaws.com/{user_pool.user_pool_id}",
            jwt_audience=[user_pool_client.user_pool_client_id],
        )

        api = apigw.HttpApi(
            self,
            "TraceFindApi",
            api_name=f"tracefind-{env_name}",
            cors_preflight=apigw.CorsPreflightOptions(
                allow_origins=["*"],
                allow_methods=[apigw.CorsHttpMethod.ANY],
                allow_headers=["Authorization", "Content-Type"],
            ),
            default_authorizer=authorizer,
        )

        def route(method: str, path: str, fn_: lambda_.Function) -> None:
            api.add_routes(
                path=path,
                methods=[apigw.HttpMethod(method)],
                integration=integ.HttpLambdaIntegration(
                    f"{fn_.node.id}Integration", fn_
                ),
            )

        route("POST", "/items", create_item)
        route("GET", "/items", get_items)
        route("GET", "/items/{id}", get_items)
        route("GET", "/items/{id}/matches", get_matches)
        route("POST", "/items/{id}/claim", claim_item)
        route("GET", "/notifications", list_notifications)
        route("POST", "/notifications/{id}/read", mark_notification_read)
        route("GET", "/admin/reports", admin_list_reports)
        route("POST", "/admin/items/{id}/archive", admin_archive)
        route("POST", "/admin/items/{id}/override-match", admin_override)
        route("POST", "/admin/items/{id}/reembed", admin_reembed)
        route("POST", "/admin/matches/{id}/reject", admin_reject)
        route("GET", "/admin/audit", admin_audit)



        self.api_url = api.api_endpoint

        self._wire_observability(
            api=api,
            handlers={
                "create_item": create_item,
                "match_items": match_items,
                "claim_item": claim_item,
                "notify_users": notify_users,
            },
            tables=[items_table, matches_table, claims_table],
            alarm_email=alarm_email,
        )

    def _wire_observability(
        self,
        *,
        api: apigw.HttpApi,
        handlers: dict[str, lambda_.Function],
        tables: list[ddb.Table],
        alarm_email: str | None,
    ) -> None:
        topic = sns.Topic(self, "AlarmTopic", topic_name=f"tracefind-alarms-{self._env_name}")
        if alarm_email:
            topic.add_subscription(sns_subs.EmailSubscription(alarm_email))
        action = cw_actions.SnsAction(topic)

        api_5xx = cw.Metric(
            namespace="AWS/ApiGateway",
            metric_name="5xx",
            dimensions_map={"ApiId": api.api_id},
            statistic="Sum",
            period=Duration.minutes(5),
        )
        api_latency = cw.Metric(
            namespace="AWS/ApiGateway",
            metric_name="Latency",
            dimensions_map={"ApiId": api.api_id},
            statistic="p95",
            period=Duration.minutes(5),
        )
        cw.Alarm(
            self,
            "Api5xxAlarm",
            metric=api_5xx,
            threshold=5,
            evaluation_periods=1,
            comparison_operator=cw.ComparisonOperator.GREATER_THAN_THRESHOLD,
            alarm_description="API Gateway 5xx > 5 in 5 min",
            treat_missing_data=cw.TreatMissingData.NOT_BREACHING,
        ).add_alarm_action(action)
        cw.Alarm(
            self,
            "ApiLatencyAlarm",
            metric=api_latency,
            threshold=2000,
            evaluation_periods=2,
            comparison_operator=cw.ComparisonOperator.GREATER_THAN_THRESHOLD,
            alarm_description="API p95 latency > 2s for 10 min",
            treat_missing_data=cw.TreatMissingData.NOT_BREACHING,
        ).add_alarm_action(action)

        for name, fn in handlers.items():
            cw.Alarm(
                self,
                f"{name}_ErrorsAlarm",
                metric=fn.metric_errors(period=Duration.minutes(5)),
                threshold=3,
                evaluation_periods=1,
                comparison_operator=cw.ComparisonOperator.GREATER_THAN_THRESHOLD,
                alarm_description=f"{name} errors > 3 in 5 min",
                treat_missing_data=cw.TreatMissingData.NOT_BREACHING,
            ).add_alarm_action(action)

        for table in tables:
            cw.Alarm(
                self,
                f"{table.node.id}_ThrottleAlarm",
                metric=table.metric(
                    "ThrottledRequests",
                    statistic="Sum",
                    period=Duration.minutes(5)
                ),
                threshold=1,
                evaluation_periods=1,
                comparison_operator=cw.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
                alarm_description=f"{table.table_name} throttling",
                treat_missing_data=cw.TreatMissingData.NOT_BREACHING,
            ).add_alarm_action(action)

        dashboard = cw.Dashboard(
            self,
            "Dashboard",
            dashboard_name=f"tracefind-{self._env_name}",
        )
        dashboard.add_widgets(
            cw.GraphWidget(
                title="API Latency p95",
                left=[api_latency],
                width=12,
            ),
            cw.GraphWidget(
                title="API 5xx",
                left=[api_5xx],
                width=12,
            ),
        )
        dashboard.add_widgets(
            cw.GraphWidget(
                title="Lambda invocations",
                left=[fn.metric_invocations() for fn in handlers.values()],
                width=12,
            ),
            cw.GraphWidget(
                title="Lambda errors",
                left=[fn.metric_errors() for fn in handlers.values()],
                width=12,
            ),
        )
