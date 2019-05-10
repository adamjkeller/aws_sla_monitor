#!/usr/bin/env python3

import boto3
from time import strftime, localtime
from dynamodb import DynamoDB

# TODO: Create a dead letter queue where we can check for failed payloads

class SNSUpdate(object):
    
    def __init__(self, topic_arn="arn:aws:sns:us-west-2:902607243125:AWS_SLA_Notifier", endpoint='localhost:8000'):
        self.client = self.sns_client()
        self.dynamo = DynamoDB(debug_mode=False, local_mode=False)
        self.dynamo_table_name = "aws_sla_change_table"
        self.topic_arn = topic_arn

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
        return_list = list()
        
        for service_desc in table_details['Items']:
            service_list.append(service_desc)

        # Removing duplicate entries. This can likely be cleaned up into a couple of python lambdas (anon function), very messy.
        for service_details in service_list:
            _serv_name = service_details['service_name']
            repeated_list = [x for x in service_list if x['service_name'] == _serv_name]
            total_count = len(repeated_list)
            if total_count > 1 or _serv_name not in [x['service_name'] for x in return_list]:
                max_date = max([x['last_updated_date'] for x in repeated_list])
                _to_return = next(x for x in service_list if x['service_name'] == _serv_name and x['last_updated_date'] == max_date)
                return_list.append(
                    _to_return
                )
        return service_list, return_list

    def clear_table(self, service_list):
        for service_info in service_list:
            self.dynamo.delete_item(self.dynamo_table_name, service_info['service_name'], service_info['last_updated_date'])

    def sns_notification(self):
        service_list, return_list = self.prepare_date()
        if return_list:
            message = self.message(return_list)
            response = self.client.publish(
                    TopicArn=self.topic_arn,
                    Message=str(message),
                    Subject="AWS SLA Update Notification"
                )
            print("Message Published! {}".format(response))
        if return_list or service_list:    
            self.clear_table(service_list)


def lambda_handler(event, context):
    SNSUpdate().sns_notification()
