# Cloudformation Deploy Steps

## Build requirements
- python3
    - virtualenv

- AWS Resources:
    - S3 bucket to host Lambda code artifact
        - ensure bucket is created in same region as deploy

## Deploy steps:
- Execute build-lambda-package.sh which will create slamonitor-lambda-code.zip
- Upload slamonitor-lambda-code.zip into S3 bucket created above
- Create new CloudFormation stack using aws-sla-monitor.yaml
- You will be prompted for the S3 bucket created above and the code package name (slamonitor-lambda-code.zip)
