#!/usr/bin/env python3

from troposphere import Output, Parameter, Ref, Template, Tags, Condition, If, Equals
from troposphere.dynamodb import (KeySchema, AttributeDefinition,
                                  ProvisionedThroughput, TimeToLiveSpecification, StreamSpecification)
from troposphere.dynamodb import Table
from os import getenv

STREAM_ENABLED = getenv('STREAM_ENABLED') or False

t = Template()

t.set_description("DynamoDB Table for AWS SLA Monitor")

tablename = t.add_parameter(Parameter(
    "DynamoTableName",
    Description="Table Name",
    Type="String",
    Default="aws_sla_monitor",
    AllowedPattern="[a-zA-Z0-9_]*",
    MinLength="3",
    MaxLength="255",
    ConstraintDescription="must contain only alphanumberic characters"
))

hashkeyname = t.add_parameter(Parameter(
    "HashKeyElementName",
    Description="HashType PrimaryKey Name",
    Type="String",
    Default="service_name",
    AllowedPattern="[a-zA-Z0-9_]*",
    MinLength="1",
    MaxLength="2048",
    ConstraintDescription="must contain only alphanumberic characters"
))

hashkeytype = t.add_parameter(Parameter(
    "HashKeyElementType",
    Description="HashType PrimaryKey Type",
    Type="String",
    Default="S",
    AllowedPattern="[S|N]",
    MinLength="1",
    MaxLength="1",
    ConstraintDescription="must be either S or N"
))

rangekeyname = t.add_parameter(Parameter(
    "RangeKeyElementName",
    Description="RangeType Key Name",
    Type="String",
    Default="last_updated_date",
    AllowedPattern="[a-zA-Z0-9_]*",
    MinLength="1",
    MaxLength="2048",
    ConstraintDescription="must contain only alphanumberic characters"
))

rangekeytype = t.add_parameter(Parameter(
    "RangeKeyElementType",
    Description="HashType Key Type",
    Type="String",
    Default="S",
    AllowedPattern="[S|N]",
    MinLength="1",
    MaxLength="1",
    ConstraintDescription="must be either S or N"
))

readunits = t.add_parameter(Parameter(
    "ReadCapacityUnits",
    Description="Provisioned read throughput",
    Type="Number",
    Default="5",
    MinValue="5",
    MaxValue="10000",
    ConstraintDescription="should be between 5 and 10000"
))

writeunits = t.add_parameter(Parameter(
    "WriteCapacityUnits",
    Description="Provisioned write throughput",
    Type="Number",
    Default="10",
    MinValue="5",
    MaxValue="10000",
    ConstraintDescription="should be between 5 and 10000"
))

ttl_enabled = t.add_parameter(Parameter(
    "TTLSettings",
    Description="TTL Settings for Attribute, Boolean to enable/disable",
    Type="String",
    Default="False",
    AllowedValues=[
        "True",
        "False"
    ],
))

myDynamoDB = t.add_resource(Table(
    "DynamoDBTable",
    TableName=Ref(tablename),
    AttributeDefinitions=[
        AttributeDefinition(
            AttributeName=Ref(hashkeyname),
            AttributeType=Ref(hashkeytype)
        ),
        AttributeDefinition(
            AttributeName=Ref(rangekeyname),
            AttributeType=Ref(rangekeytype)
        ), 
    ],
    KeySchema=[
        KeySchema(
            AttributeName=Ref(hashkeyname),
            KeyType="HASH"
        ),
        KeySchema(
            AttributeName=Ref(rangekeyname),
            KeyType="RANGE"
        ),
    ],
    ProvisionedThroughput=ProvisionedThroughput(
        ReadCapacityUnits=Ref(readunits),
        WriteCapacityUnits=Ref(writeunits)
    ),
    TimeToLiveSpecification=TimeToLiveSpecification(
        AttributeName="expiration_time",
        Enabled=Ref(ttl_enabled)
    ),
    Tags=Tags(
        Environment="Production",
        Name="AWS SLA Monitor"
    )
))

if STREAM_ENABLED:
    add_stream = myDynamoDB.StreamSpecification = StreamSpecification(
        StreamViewType="NEW_IMAGE"
    )

t.add_output(Output(
    "TableName",
    Value=Ref(myDynamoDB),
    Description="Table name of the newly create DynamoDB table",
))

print(t.to_yaml())