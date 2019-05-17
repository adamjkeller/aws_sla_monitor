#!/usr/bin/env python3

from os import getenv
from aws_crawler import AwsSlaCrawler

def lambda_handler(event, context):
    _debug = True # TODO: make env vars
    _local_mode = False
    _dynamo_table_name = getenv("STACK_NAME") 
    AwsSlaCrawler(dynamo_table_name=_dynamo_table_name, local_mode=_local_mode, debug_mode=_debug).main()    

if __name__ == '__main__':
    lambda_handler("test1", "test2")
