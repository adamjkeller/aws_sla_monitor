#!/usr/bin/env bash

# To get dynamo local running on docker: docker run -p 8000:8000 amazon/dynamodb-local

# Create the test table
aws dynamodb create-table \
    --endpoint-url http://localhost:8000 \
    --table-name aws_sla_monitor \
    --attribute-definitions \
        AttributeName=service_name,AttributeType=S \
        AttributeName=last_updated_date,AttributeType=S \
    --key-schema AttributeName=service_name,KeyType=HASH AttributeName=last_updated_date,KeyType=RANGE \
    --provisioned-throughput ReadCapacityUnits=2,WriteCapacityUnits=2

# List the tables to confirm that it exists
aws dynamodb list-tables --endpoint-url http://localhost:8000

# Update record for testing
#aws dynamodb put-item --endpoint-url http://localhost:8000 --table-name AWS_SLA_MONITOR --item file://update.json
