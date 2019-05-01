#!/usr/bin/env python3

from aws_crawler import AwsSlaCrawler

if __name__ == '__main__':
    _debug = True
    _local_mode = False
    AwsSlaCrawler(local_mode=_local_mode, debug_mode=_debug).main()