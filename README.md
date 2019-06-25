AWS SLA Monitor
==============================

What Is This?
-------------

AWS SLA Monitor will monitor all published SLA's update dates via the [website](https://aws.amazon.com/legal/service-level-agreements/)

It will track if an update has been made to any of the listed SLA's and notify the users you define via email when one or more have been updated.


How To Use This
---------------

The CDK Way:

1. In the root of the project, run `./package_code.py`
    - This will compile the lambda packages into zip files to be deployed.  
2. Navigate to the cdk directory, and modify the environment variables in the `env_vars.sh` file. Here are the following that you should update/replace:
    ```
    export STACK_NAME='my-sla-monitor'
    export EMAIL_NOTIFICATION='group-email@email-endpoint.com'
    ```
3. Source the env_vars.sh variables (`source ./env_vars.sh`) 

4. Now, let's confirm that the cdk can compile the the code as CloudFormation templates:
    ```
    docker run -v $(pwd):/cdk \
    -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
    -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    -e STACK_NAME=$STACK_NAME \
    -e EMAIL_NOTIFICATION=$EMAIL_NOTIFICATION \
    -e GIT_HASH=$GIT_HASH \
    -it adam9098/aws-cdk:$CDK_VERSION synth
    ```

5) You should see stack-name.template.json files that were outputted to the cdk.out directory. These are the CloudFormation templates that will be used to be deployed via the cdk.

6) Next, run `cdk diff`, this will provide outputs via the command line of what you are building.

    ```
    docker run -v $(pwd):/cdk \
    -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
    -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    -e STACK_NAME=$STACK_NAME \
    -e EMAIL_NOTIFICATION=$EMAIL_NOTIFICATION \
    -e GIT_HASH=$GIT_HASH \
    -it adam9098/aws-cdk:$CDK_VERSION diff
    ```

7) Assuming everything looks good, run `cdk deploy`.

    ```
    docker run -v $(pwd):/cdk \
    -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
    -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    -e STACK_NAME=$STACK_NAME \
    -e EMAIL_NOTIFICATION=$EMAIL_NOTIFICATION \
    -e GIT_HASH=$GIT_HASH \
    -it adam9098/aws-cdk:$CDK_VERSION deploy
    ```
8) That's it! The email address added to the env variables will receive an email from SNS to accept the subscription. 

The CloudFormation way:

1) Navigate to the `cfn-native` directory, and follow the Instructions.md there.