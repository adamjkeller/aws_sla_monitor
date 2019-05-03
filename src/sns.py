#!/usr/bin/env python3

import boto3
from time import strftime, localtime
from dynamodb import DynamoDB

class SNSUpdate(object):
    
    def __init__(self, endpoint='localhost:8000'):
        self.client = self.sns_client()
        self.dynamo = DynamoDB(debug_mode=False, local_mode=False)
        self.dynamo_table_name = "aws_sla_change_table"
        self.topic_arn = "arn:aws:sns:us-west-2:902607243125:AWS_SLA_Notifier"

    def sns_client(self):
        return boto3.client('sns')

    def message(self, service_list):
        _message = ""
        for service_info in service_list:
            updated_date = strftime('%B %d, %Y', localtime(int(service_info['last_updated_date'])))
            _message += "{}: {}\n".format(service_info['service_name'], updated_date)

        return """An update has been made to one or more of the published SLA pages for an AWS Service. Please review the below services that had a change:\n\n{}\n\nCheck SLA's here: https://aws.amazon.com/legal/service-level-agreements/""".format(_message)

    def prepare_date(self):
        table_details = self.dynamo.scan_table(self.dynamo_table_name)
        service_list = list()
        for service_desc in table_details['Items']:
            service_list.append(service_desc)
        return service_list

    def sns_notification(self):
        service_list = self.prepare_date()
        message = self.message(service_list)
        self.client.publish(
                TopicArn=self.topic_arn,
                Message=str(message),
                Subject="AWS SLA Update Notification"
            )


def lambda_handler(event, context):
    SNSUpdate().sns_notification()
