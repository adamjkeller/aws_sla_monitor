#!/usr/bin/env python3

import boto3
from time import strftime, localtime

class SNSUpdate(object):
    
    def __init__(self):
        self.client = self.sns_client()
        self.topic_arn = "arn:aws:sns:us-west-2:902607243125:AWS_SLA_Notifier"

        
    def sns_client(self):
        return boto3.client('sns')

    def message(self, service_list):
        _message = ""
        for service_info in service_list:
            for service_name, updated_date in service_info.items():
                updated_date = strftime('%B %d, %Y', localtime(int(updated_date)))
                _message += "{}: {}\n".format(service_name, updated_date)

        return """A change has been made to one or more of the SLA pages for an AWS Service. Please review the below services that had a change:\n\n{}""".format(_message)

    def sns_notification(self, service_list):
        message = self.message(service_list)
        self.client.publish(
                TopicArn=self.topic_arn,
                Message=str(message),
                Subject="AWS SLA Update Notification"
            )


def lambda_handler(event, context):
    updated_service_list = list()
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            ddb_record = record['dynamodb']['Keys']
            updated_service_list.append({ddb_record['service_name']['S']: ddb_record['last_updated_date']['S']})
            
    SNSUpdate().sns_notification(service_list=updated_service_list)
