#!/usr/bin/env python3

from aws_crawler import AwsSlaCrawler

def lambda_handler(event, context):
    _debug = True
    _local_mode = False
    AwsSlaCrawler(local_mode=_local_mode, debug_mode=_debug).main()    

if __name__ == '__main__':
    lambda_handler("test1", "test2")