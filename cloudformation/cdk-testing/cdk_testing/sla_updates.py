#!/usr/bin/env python3
import os
import sh
from aws_cdk import (
    aws_lambda, 
    aws_events,
    aws_events_targets,
    aws_s3,
    aws_s3_deployment,
    aws_logs,
    aws_dynamodb,
    cdk
)


class AWSSlaStreamMonitor(cdk.Construct):

    def __init__(self, scope: cdk.Construct, id: str, stack_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        def zip_package():
            cwd = os.getcwd()
            file_name = 'aws-sla-stream-monitor-cdk.zip'
            zip_file = cwd + '/' + file_name

            os.chdir('../../package/')
            sh.zip('-r9', zip_file, '.')
            os.chdir('../src/')
            sh.zip('-gr', zip_file, './')
            os.chdir(cwd)

            return file_name, zip_file

        _, zip_file = zip_package()

        lambda_function = aws_lambda.Function(
            self, "LambdaFunction",
            function_name="{}-aws-sla-stream-monitor-cdk".format(stack_name),
            code=aws_lambda.AssetCode(zip_file),
            handler="stream_processor.lambda_handler",
            runtime=aws_lambda.Runtime.PYTHON37,
            description="Monitors DynamoDB stream from SLA Monitor and updates a DynamoDB Table with any changes",
            environment={
                "STACK_NAME": stack_name,
                "LOCAL_MODE": "False",
            },
            memory_size=128,
            timeout=90,
        )

        lambda_function.add_event_source()

#        dynamo_backend = aws_dynamodb.Table(
#            self, "DynamoTable",
#            table_name="{}-aws-sla-monitor-cdk".format(stack_name),
#            partition_key={"name": "service_name", "type": aws_dynamodb.AttributeType.String},
#            sort_key={"name": "last_updated_date", "type": aws_dynamodb.AttributeType.String},
#            #read_capacity=5,
#            #write_capacity=5,
#            billing_mode=aws_dynamodb.BillingMode.PayPerRequest,
#            stream_specification=aws_dynamodb.StreamViewType.NewImage
#        )
#
#        dynamo_backend.grant_read_write_data(lambda_function.role)