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

# TODO: Fix all code packaging, right now duplicated and zipping all the things.

class BaseModule(cdk.Stack):

    def __init__(self, scope: cdk.Stack, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        def zip_package():
            cwd = os.getcwd()
            file_name = 'dynamo-layer.zip'
            zip_file = cwd + '/' + file_name

            os.chdir('../../src/')
            sh.zip('-r9', zip_file, 'dynamodb.py')
            os.chdir(cwd)

            return file_name, zip_file

        _, zip_file = zip_package()

        code_path = "/Users/keladam/code/sla-monitor/"

        self.dynamodb_lambda_layer = aws_lambda.LayerVersion(
            self, "DynamoDBHelperLambdaLayer",
            code = aws_lambda.AssetCode(zip_file),
            compatible_runtimes = [aws_lambda.Runtime.PYTHON37],
            description = "DynamoDB Shared Library"
        )

class SLAMonitor(cdk.Stack):

    def __init__(self, scope: cdk.Stack, id: str, dynamodb_lambda_layer: object, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.dynamodb_lambda_layer = dynamodb_lambda_layer

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

        self.sla_monitor_dynamo_table = aws_dynamodb.Table(
            self, "DynamoTable{}".format("SLAMonitor"),
            table_name=self.stack_name + "-aws-sla-monitor-cdk",
            billing_mode=aws_dynamodb.BillingMode.PayPerRequest,
            stream_specification=aws_dynamodb.StreamViewType.NewImage,
            partition_key={"name": "service_name", "type": aws_dynamodb.AttributeType.String},
            sort_key={"name": "last_updated_date", "type": aws_dynamodb.AttributeType.String},
        )

        self.sla_monitor_lambda_function = aws_lambda.Function(
            self, "SLAMonitorLambdaFunction",
            function_name="{}-aws-sla-monitor-cdk".format(self.stack_name),
            code=aws_lambda.AssetCode(zip_file),
            handler="main.lambda_handler",
            runtime=aws_lambda.Runtime.PYTHON37,
            tracing=aws_lambda.Tracing.Active,
            layers=[
                self.dynamodb_lambda_layer
            ],
            description="Monitors AWS SLA Pages and updates DynamoDB Table when SLAs update",
            environment={
                "STACK_NAME": self.stack_name,
                "LOCAL_MODE": "False",
                "DYNAMO_TABLE_NAME": self.stack_name + "-" + "aws-sla-monitor-cdk"
            },
            memory_size=128,
            timeout=90,
        )

        # Permissions to access sla_monitor dynamo table
        self.sla_monitor_dynamo_table.grant_read_write_data(self.sla_monitor_lambda_function.role)

        self.sla_monitor_cw_event_rule = aws_events.EventRule(
            self, "LambdaCWEventRuleSLAMonitor",
            description="Scheduled event to trigger AWS SLA monitor",
            enabled=True,
            #schedule_expression='cron(0 22 */3 * ? *)',
            schedule_expression='cron(*/8 * * * ? *)',            
            targets=[
                aws_events_targets.LambdaFunction(handler=self.sla_monitor_lambda_function)
            ],
        )

class StreamMonitor(cdk.Stack):

    def __init__(self, scope: cdk.Stack, id: str, sla_monitor_dynamo_table, dynamodb_lambda_layer, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.sla_monitor_dynamo_table = sla_monitor_dynamo_table
        self.dynamodb_lambda_layer = dynamodb_lambda_layer

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

        self.sla_stream_monitor_lambda_function = aws_lambda.Function(
            self, "StreamMonitorLambdaFunction",
            function_name="{}-aws-sla-stream-monitor-cdk".format(self.stack_name),
            code=aws_lambda.AssetCode(zip_file),
            handler="stream_processor.lambda_handler",
            runtime=aws_lambda.Runtime.PYTHON37,
            layers=[self.dynamodb_lambda_layer],
            description="Monitors DynamoDB stream from SLA Monitor and updates a DynamoDB Table with any changes",
            environment={
                "STACK_NAME": self.stack_name,
                "DYNAMO_TABLE_NAME": self.stack_name + "-aws-sla-stream-monitor-cdk"
            },
            memory_size=128,
            timeout=90,
        )

        self.sla_stream_monitor_dynamo_table = aws_dynamodb.Table(
            self, "DynamoTable{}".format("SLAStreamMonitor"),
            table_name=self.stack_name + "-aws-sla-stream-monitor-cdk",
            billing_mode=aws_dynamodb.BillingMode.PayPerRequest,
            partition_key={"name": "service_name", "type": aws_dynamodb.AttributeType.String},
            sort_key={"name": "last_updated_date", "type": aws_dynamodb.AttributeType.String},
        )

        # Permissions to access stream_monitor dynamo table
        self.sla_stream_monitor_dynamo_table.grant_read_write_data(self.sla_stream_monitor_lambda_function.role)

        # Event source for stream monitor lambda function from sla monitor dynamodb stream
        self.sla_stream_monitor_lambda_function.add_event_source(
            aws_lambda_event_sources.DynamoEventSource(
                table=self.sla_monitor_dynamo_table, starting_position=aws_lambda.StartingPosition.Latest
            )
        )

class SLAChangeNotifier(cdk.Stack):

    def __init__(self, scope: cdk.Stack, id: str, sla_stream_monitor_dynamo_table, dynamodb_lambda_layer, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.sla_stream_monitor_dynamo_table = sla_stream_monitor_dynamo_table
        self.dynamodb_lambda_layer = dynamodb_lambda_layer

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

        self.sns_topic = aws_sns.Topic(
            self, "SNSTopic",
            display_name="SLA Notification Topic",
            topic_name=self.stack_name + "-" + "aws-sla-monitor-notification-cdk"
        )

        self.subscribe_to_topic = aws_sns.Subscription(
            self, "TopicSubscribe",
            endpoint='keladam@amazon.com',
            protocol=aws_sns.SubscriptionProtocol.Email,
            topic=self.sns_topic
        )

        self.sla_notifier_lambda_function = aws_lambda.Function(
            self, "SLANotifierLambdaFunction",
            function_name="{}-aws-sla-notifier-cdk".format(self.stack_name),
            code=aws_lambda.AssetCode(zip_file),
            handler="sns.lambda_handler",
            runtime=aws_lambda.Runtime.PYTHON37,
            layers=[self.dynamodb_lambda_layer],
            description="Notifies SNS Topic if SLAs change",
            environment={
                "STACK_NAME": self.stack_name,
                "SNS_TOPIC_ARN": self.sns_topic.topic_arn,
                "DYNAMO_TABLE_NAME": self.stack_name + "-" + "aws-sla-stream-monitor-cdk"
            },
            memory_size=128,
            timeout=90,
        )

        # TODO: Make into reusable function
        self.notifier_cw_event_rule = aws_events.EventRule(
            self, "LambdaCWEventRuleSLANotifier",
            description="Scheduled event to trigger AWS SLA monitor",
            enabled=True,
            #schedule_expression='cron(10 22 */3 * ? *)',
            schedule_expression='cron(*/6 * * * ? *)',            
            targets=[
                aws_events_targets.LambdaFunction(handler=self.sla_notifier_lambda_function)
            ],
        )

        # Permissions to access stream_monitor dynamo table
        self.sla_stream_monitor_dynamo_table.grant_read_write_data(self.sla_notifier_lambda_function.role)


class MainApp(cdk.App):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        _stack_name = "keladam-test"

        self.base_stack = BaseModule(self, _stack_name + "-base")

        self.sla_monitor = SLAMonitor(self, _stack_name + "-monitor", dynamodb_lambda_layer=self.base_stack.dynamodb_lambda_layer)

        self.stream_monitor = StreamMonitor(
            self, _stack_name + "-stream", 
            sla_monitor_dynamo_table=self.sla_monitor.sla_monitor_dynamo_table,
            dynamodb_lambda_layer=self.base_stack.dynamodb_lambda_layer
        )

        self.change_notifier = SLAChangeNotifier(
            self, "change-notifier", 
            sla_stream_monitor_dynamo_table=self.stream_monitor.sla_stream_monitor_dynamo_table,
            dynamodb_lambda_layer=self.base_stack.dynamodb_lambda_layer
        )


app = MainApp()
app.run()