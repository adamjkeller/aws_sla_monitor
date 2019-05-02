#!/usr/bin/env bash

cd src/package/
zip -r9 ../function.zip .
zip -g function.zip aws_crawler.py dynamodb.py main.py
aws lambda update-function-code --function-name AWS_SLA_MONITOR --zip-file fileb://function.zip