#!/usr/bin/env python3

import os
import sh

class PackageCode(object):

    def __init__(self, force_deploy=False):
        self.force_deploy = force_deploy
        self.git_hash = sh.git("rev-parse", "--short=7", "HEAD").strip()
        self.code_dir = 'src/'
        self.to_package = {
            'sla-monitor.zip': [{'file': 'main.py'}, {'file': 'aws_crawler.py'}, {'file': 'dynamodb.py'}, {'dir': 'package/'}],
            'stream-monitor.zip': [{'file': 'dynamodb.py'}, {'file': 'stream_processor.py'}],
            'change-notifier.zip': [{'file': 'sns.py'},{'file': 'dynamodb.py'}],
        }

    def prepare_path(self, file_name):
        cwd = os.getcwd()
        file_name = '{}-{}'.format(self.git_hash, file_name)
        zip_file = cwd + '/cdk/' + file_name
        return zip_file, cwd

    def package_zip(self, file_name, files):
        zip_file, cwd = self.prepare_path(file_name)

        if os.path.isfile(zip_file) and not self.force_deploy:
            print("==> File {} exists, moving on.".format(zip_file))
            return zip_file

        print("==> Packaging the following: {}".format(file_name))
        for file_info in files:
            for file_type, name in file_info.items():
                if file_type == 'file':
                    print("Adding file {} to {}".format(name, zip_file))
                    os.chdir(self.code_dir)
                    sh.zip('-gr9', zip_file, name)
                    os.chdir(cwd)
                elif file_type == 'dir':
                    print("Adding directory contents of {} to {}".format(name, zip_file))
                    os.chdir(name)
                    sh.zip('-gr9', zip_file, '.')
                    os.chdir(cwd)
                else:
                    print("something went wrong")

        return zip_file

    def package(self):
        for file_name, packages in self.to_package.items():
            self.package_zip(file_name, packages)


if __name__ == '__main__':
    from sys import argv

    try:
        if argv[1]:
            _force_deploy = True
    except:
        _force_deploy = False

    code = PackageCode(force_deploy=_force_deploy)
    code.package()