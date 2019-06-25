#!/usr/bin/env bash

if [[ $1 == 'package' ]];then
  pushd ../
  ./package_code.py $2
  popd
fi

source ./env_vars.sh

docker run -v $(pwd):/cdk \
-e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
-e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
-e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
-e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
-e STACK_NAME=$STACK_NAME \
-e EMAIL_NOTIFICATION=$EMAIL_NOTIFICATION \
-e GIT_HASH=$GIT_HASH \
-it adam9098/aws-cdk:$CDK_VERSION synth
