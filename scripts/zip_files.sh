#!/usr/bin/env bash

pushd package/
zip -r9 ../function.zip .
popd
pushd src/
zip -g ../function.zip aws_crawler.py dynamodb.py main.py
popd
aws lambda update-function-code --function-name AWS_SLA_MONITOR --zip-file fileb://function.zip

