#!/usr/bin/env python3

from boto3.dynamodb.conditions import Key, Attr
import boto3

# TODO: Cleanup dynamo table name parameter

class DynamoDB(object):

    def __init__(self, debug_mode, dynamo_table, local_mode=False, endpoint='localhost:8000'):
        self.debug_mode = debug_mode
        self.endpoint = endpoint 
        self.local_mode = local_mode
        self.dynamo_client = self.set_dynamo_client(endpoint=self.endpoint)
        self.dynamo_table = dynamo_table
        self.dynamo_table_details = {
            "Name": dynamo_table, 
            "Attributes": {
                "service_name": "HASH",
                "last_updated_date": "RANGE"
            }
        }        

    def set_dynamo_client(self, endpoint):
        if self.local_mode: 
            endpoint = "http://" + self.endpoint
        else:
            endpoint = None

        return boto3.resource("dynamodb", endpoint_url=endpoint)

    def scan_table(self, table_name):
        return self.dynamo_client.Table(table_name).scan()

    def query_db(self, service_name, updated_date):
        return self.dynamo_client.Table(self.dynamo_table_details['Name']).query(
                    KeyConditionExpression=Key('service_name').eq(service_name)
                )

    def compare_against_current_dataset(self, db_results, current_epoch):
        attributes = db_results['Items']
        time_stamps = list()
        if db_results['Count'] > 0:
            for values in attributes:
                time_stamps.append(values['last_updated_date'])
        
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
            "Updating Database with the following attributes: service_name: {}, last_updated_date: {}".format(
                service_name, epoch
            )   
        )

        print(
            self.dynamo_client.Table(self.dynamo_table_details['Name']).put_item(
                Item={
                    'service_name': service_name,
                    'last_updated_date': str(epoch)
                },
            )
        )

    def update_stream_data_set(self, service_name, epoch_changed_date, epoch_expiry, table_name):
        print(
            self.dynamo_client.Table(table_name).put_item(
                Item={
                    'service_name': service_name,
                    'last_updated_date': str(epoch_changed_date),
                    'expiration_time': int(epoch_expiry)
                },
            )
        )    

    def delete_item(self, table_name, service_name, last_updated_date):
        print(
            self.dynamo_client.Table(table_name).delete_item(
                Key={
                    'service_name': service_name,
                    'last_updated_date': str(last_updated_date)                    
                }
            )
        )