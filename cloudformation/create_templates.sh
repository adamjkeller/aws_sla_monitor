#!/usr/bin/env bash

# Create table for SLA Monitor Lambda
export STREAM_ENABLED=True
./troposphere/dynamodb.py > ./sla_monitor_dynamodb_template.yaml
export STREAM_ENABLED=False

# Create table for change table notification Lambda
./troposphere/dynamodb.py > ./sla_change_dynamodb_template.yaml
