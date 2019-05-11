#!/usr/bin/env python3
import os
import sh
from aws_cdk import (
    aws_lambda,
    aws_lambda_event_sources, 
    aws_events,
    aws_events_targets,
    aws_s3,
    aws_s3_deployment,
    aws_logs,
    aws_dynamodb,
    aws_sns,
    cdk
)


class AWSSlaMonitor(cdk.Construct):

    def __init__(self, scope: cdk.Construct, id: str, stack_name: str) -> None:
        super().__init__(scope, id)

        def zip_package():
            cwd = os.getcwd()
            file_name = 'aws-sla-monitor-cdk.zip'
            zip_file = cwd + '/' + file_name

            os.chdir('../../package/')
            sh.zip('-r9', zip_file, '.')
            os.chdir('../src/')
            sh.zip('-gr', zip_file, './')
            os.chdir(cwd)

            return file_name, zip_file

        _, zip_file = zip_package()

        # TODO: Move to it's own construct at some point and make more dynamic
        def dynamo_table_create(table_name, pay_per_request, stream_enabled):

            if pay_per_request:
                billing_mode = aws_dynamodb.BillingMode.PayPerRequest
            else:
                billing_mode = aws_dynamodb.BillingMode.PROVISIONED

            if stream_enabled:
                stream_spec = aws_dynamodb.StreamViewType.NewImage
            else:
                stream_spec = None

            dynamo = aws_dynamodb.Table(
                self, "DynamoTable{}".format(table_name),
                table_name=stack_name + "-" + table_name,
                billing_mode=billing_mode,
                stream_specification=stream_spec,
                partition_key={"name": "service_name", "type": aws_dynamodb.AttributeType.String},
                sort_key={"name": "last_updated_date", "type": aws_dynamodb.AttributeType.String},
            )

            return dynamo

        sla_monitor_lambda_function = aws_lambda.Function(
            self, "SLAMonitorLambdaFunction",
            function_name="{}-aws-sla-monitor-cdk".format(stack_name),
            code=aws_lambda.AssetCode(zip_file),
            handler="main.lambda_handler",
            runtime=aws_lambda.Runtime.PYTHON37,
            description="Monitors AWS SLA Pages and updates DynamoDB Table when SLAs update",
            environment={
                "STACK_NAME": stack_name,
                "LOCAL_MODE": "False",
                "DYNAMO_TABLE_NAME": stack_name + "-" + "aws-sla-monitor-cdk"
            },
            memory_size=128,
            timeout=90,
        )

        sla_stream_monitor_lambda_function = aws_lambda.Function(
            self, "StreamMonitorLambdaFunction",
            function_name="{}-aws-sla-stream-monitor-cdk".format(stack_name),
            code=aws_lambda.AssetCode(zip_file),
            handler="stream_processor.lambda_handler",
            runtime=aws_lambda.Runtime.PYTHON37,
            description="Monitors DynamoDB stream from SLA Monitor and updates a DynamoDB Table with any changes",
            environment={
                "STACK_NAME": stack_name,
                "DYNAMO_TABLE_NAME": stack_name + "-" + "aws-sla-stream-monitor-cdk"
            },
            memory_size=128,
            timeout=90,
        )

        sns_topic = aws_sns.Topic(
            self, "SNSTopic",
            display_name="SLA Notification Topic",
            topic_name=stack_name + "-" + "aws-sla-monitor-notification-cdk"
        )

        subscribe_to_topic = aws_sns.Subscription(
            self, "TopicSubscribe",
            endpoint='keladam@amazon.com',
            protocol=aws_sns.SubscriptionProtocol.Email,
            topic=sns_topic
        )

        sla_notifier_lambda_function = aws_lambda.Function(
            self, "SLANotifierLambdaFunction",
            function_name="{}-aws-sla-notifier-cdk".format(stack_name),
            code=aws_lambda.AssetCode(zip_file),
            handler="sns.lambda_handler",
            runtime=aws_lambda.Runtime.PYTHON37,
            description="Notifies SNS Topic if SLAs change",
            environment={
                "STACK_NAME": stack_name,
                "SNS_TOPIC_ARN": sns_topic.topic_arn,
                "DYNAMO_TABLE_NAME": stack_name + "-" + "aws-sla-stream-monitor-cdk"
            },
            memory_size=128,
            timeout=90,
        )

        # TODO: Make into reusable function
        notifier_cw_event_rule = aws_events.EventRule(
            self, "LambdaCWEventRuleSLANotifier",
            description="Scheduled event to trigger AWS SLA monitor",
            enabled=True,
            schedule_expression='cron(10 22 */3 * ? *)',
            targets=[
                aws_events_targets.LambdaFunction(handler=sla_notifier_lambda_function)
            ],
        )

        sla_monitor_cw_event_rule = aws_events.EventRule(
            self, "LambdaCWEventRuleSLAMonitor",
            description="Scheduled event to trigger AWS SLA monitor",
            enabled=True,
            schedule_expression='cron(0 22 */3 * ? *)',
            targets=[
                aws_events_targets.LambdaFunction(handler=sla_monitor_lambda_function)
            ],
        )        

        # Create DynamoDB Backends
        sla_monitor_dynamo_backend = dynamo_table_create(table_name="aws-sla-monitor-cdk", stream_enabled=True, pay_per_request=True)
        sla_stream_monitor_dynamo_backend = dynamo_table_create(table_name="aws-sla-stream-monitor-cdk", stream_enabled=False, pay_per_request=True)

        # Permissions to access sla_monitor dynamo table
        sla_monitor_dynamo_backend.grant_read_write_data(sla_monitor_lambda_function.role)

        # Permissions to access stream_monitor dynamo table
        sla_stream_monitor_dynamo_backend.grant_read_write_data(sla_stream_monitor_lambda_function.role)
        sla_stream_monitor_dynamo_backend.grant_read_write_data(sla_notifier_lambda_function.role)

        # Event source for stream monitor lambda function from sla monitor dynamodb stream
        sla_stream_monitor_lambda_function.add_event_source(
            aws_lambda_event_sources.DynamoEventSource(
                table=sla_monitor_dynamo_backend, starting_position=aws_lambda.StartingPosition.Latest
            )
        )

        # Grant access from notifier lambda to sns
        sns_topic.grant_publish(sla_notifier_lambda_function.role)
