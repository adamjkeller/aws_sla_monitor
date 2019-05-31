#!/usr/bin/env python3

import os
import sh

class PackageCode(object):

    def __init__(self):
        self.git_hash = sh.git("rev-parse", "--short=7", "HEAD").strip()

    def prepare_path(self, file_name):
        cwd = os.getcwd()
        file_name = '{}-{}'.format(self.git_hash, file_name)
        zip_file = cwd + '/' + file_name
        return zip_file

    def sla_monitor_code(self):
        zip_file = self.prepare_path("aws-sla-monitor-cdk.zip")

        os.chdir('../package/')
        sh.zip('-r9', zip_file, '.')
        os.chdir('../src/')
        sh.zip('-gr', zip_file, 'main.py')
        sh.zip('-gr', zip_file, 'aws_crawler.py')
        sh.zip('-gr', zip_file, 'dynamodb.py')
        os.chdir(cwd)

        return zip_file

    zip_file = zip_package()