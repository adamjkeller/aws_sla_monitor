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


class AWSSlaMonitor(cdk.Stack):

    def __init__(self, app: cdk.App, id: str, **kwargs) -> None:
        super().__init__(app, id, **kwargs)

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

        #### IF WE WANT TO UPLOAD FILE TO S3 ON OUR OWN ###############
        # Ideally, python code should prob live in it's own repo/deploy process
        #bucket_encryption = aws_s3.BucketEncryption.Kms
        #
        #s3_public_access = aws_s3.BlockPublicAccess(
        #    block_public_acls=True,
        #    block_public_policy=True,
        #)
        #
        #s3_bucket = aws_s3.Bucket(
        #    self, "LambdaS3Bucket",
        #    block_public_access=s3_public_access,
        #    bucket_name="{}-aws-sla-monitor-cdk".format(self.stack_name),
        #    encryption=bucket_encryption,
        #    versioned=True
        #)
        #
        #s3_bucket_deployment = aws_s3_deployment.BucketDeployment(
        #    self, "LambdaCodeDeployment",
        #    source=aws_s3_deployment.Source.asset(zip_file),
        #    destination_bucket=s3_bucket,
        #)
        #
        #lambda_code = aws_lambda.Code.bucket(
        #    bucket=s3_bucket,
        #    key=file_name,
        #)
        ################################################################

        lambda_function = aws_lambda.Function(
            self, "LambdaFunction",
            function_name="{}-aws-sla-monitor-cdk".format(self.stack_name),
            code=aws_lambda.AssetCode(zip_file),
            #code=lambda_code,
            handler="main.lambda_handler",
            runtime=aws_lambda.Runtime.PYTHON37,
            description="Monitors AWS SLA Pages and updates DynamoDB Table when SLAs update",
            environment={
                "STACK_NAME": self.stack_name,
                "LOCAL_MODE": "False",
            },
            #log_retention_days=aws_logs.RetentionDays.TwoWeeks,
            memory_size=128,
            timeout=90,
        )

        cw_event_rule = aws_events.EventRule(
            self, "LambdaCWEventRule",
            description="Scheduled event to trigger AWS SLA monitor",
            enabled=True,
            schedule_expression='cron(0 22 */3 * ? *)',
            targets=[
                aws_events_targets.LambdaFunction(handler=lambda_function)
            ],
        )

        dynamo_backend = aws_dynamodb.Table(
            self, "DynamoTable",
            table_name="{}-aws-sla-monitor-cdk".format(self.stack_name),
            partition_key={"name": "service_name", "type": aws_dynamodb.AttributeType.String},
            sort_key={"name": "last_updated_date", "type": aws_dynamodb.AttributeType.String},
            #read_capacity=5,
            #write_capacity=5,
            billing_mode=aws_dynamodb.BillingMode.PayPerRequest,
            stream_specification=aws_dynamodb.StreamViewType.NewImage
        )

        dynamo_backend.grant_read_write_data(lambda_function.role)