#!/usr/bin/env python3

from time import strftime
from dynamodb import DynamoDB

class ReadDynamoStream(object):
    
    def __init__(self, event_details, debug_mode=False, local_mode=False):
        self.event_details = event_details
        self.dynamo = DynamoDB(debug_mode=debug_mode, local_mode=local_mode)
        self.epoch_time = self.setup_epoch_time()
        self.dynamo_table_name = "aws_sla_change_table"

    def setup_epoch_time(self):
        # Adding thirty minutes to ensure automation has time to come in and process data prior to ttl expiry
        return int(strftime("%s")) + 1800
        
    def prepare_data(self):
        updated_service_list = list()
        for record in self.event_details['Records']:
            if record['eventName'] == 'INSERT':
                ddb_record = record['dynamodb']['Keys']
                updated_service_list.append({ddb_record['service_name']['S']: ddb_record['last_updated_date']['S']})

        return updated_service_list
                
    def update_tables(self, service_list):
        for service in service_list:
            for service_name, updated_date in service.items():
                self.dynamo.update_stream_data_set(service_name=service_name, epoch_changed_date=updated_date, epoch_expiry=self.epoch_time, table_name=self.dynamo_table_name)

    def main(self):
        data_list = self.prepare_data()
        self.update_tables(service_list=data_list)

    
def lambda_handler(event, context):
    ReadDynamoStream(event_details=event).main()
