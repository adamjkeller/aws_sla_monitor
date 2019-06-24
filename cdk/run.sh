#!/usr/bin/env bash

source ./env_vars.sh

docker run -v $(pwd):/cdk \
-e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
-e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
-e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
-e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
-e STACK_NAME=$STACK_NAME \
-e EMAIL_NOTIFICATION=$EMAIL_NOTIFICATION \
-e GIT_HASH=$GIT_HASH \
-it adam9098/aws-cdk:v0.33.0 diff
