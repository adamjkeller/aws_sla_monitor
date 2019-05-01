#!/usr/bin/env python3

from boto3.dynamodb.conditions import Key, Attr
import boto3


class DynamoDB(object):

    def __init__(self, debug_mode):
        self.debug_mode = debug_mode
        self.dynamo_client = self.set_dynamo_client(endpoint='localhost:8000')
        self.dynamo_table_details = {
            "Name": "AWS_SLA_MONITOR", 
            "Attributes": {
                "SERVICE_NAME": "HASH",
                "LAST_UPDATED_DATE": "RANGE"
            }
        }        

    def set_dynamo_client(self, endpoint):
        return boto3.resource('dynamodb', endpoint_url="http://{}".format(endpoint))  

    def query_db(self, service_name, updated_date):
        return self.dynamo_client.Table(self.dynamo_table_details['Name']).query(
                    KeyConditionExpression=Key('SERVICE_NAME').eq(service_name)
                )

    def compare_against_current_dataset(self, db_results, current_epoch):
        attributes = db_results['Items']
        time_stamps = list()
        if db_results['Count'] > 0:
            for values in attributes:
                time_stamps.append(values['LAST_UPDATED_DATE'])
        
        if str(current_epoch) in time_stamps:
            if self.debug_mode:
                print("Date has not changed, no updates necessary")
                print("Current Date: {}\nList of dates for this service: {}".format(current_epoch, time_stamps))
            return False
        else:
            print("Date has changed, updates are necessary")
            print("Current Date: {}\nList of dates for this service: {}".format(current_epoch, time_stamps))
            return True

    def update_data_set(self, service_name, epoch):
        print(
            "Updating Database with the following attributes: SERVICE_NAME: {}, LAST_UPDATED_DATE: {}".format(
                service_name, epoch
            )   
        )

        print(
            self.dynamo_client.Table(self.dynamo_table_details['Name']).put_item(
                Item={
                    'SERVICE_NAME': service_name,
                    'LAST_UPDATED_DATE': str(epoch)
                },
            )
        )