AWS SLA Monitor
==============================

[![TravisCI](https://travis-ci.org/uber/Python-Sample-Application.svg?branch=master)](https://travis-ci.org/uber/Python-Sample-Application)
[![Coverage Status](https://coveralls.io/repos/uber/Python-Sample-Application/badge.png)](https://coveralls.io/r/uber/Python-Sample-Application)

What Is This?
-------------

AWS SLA Monitor will monitor all published SLA's via the website: <url-here>

It will track if an update has been made to any of the listed SLA's and notify the users you define via email when one or more have been updated.


How To Use This
---------------

1. To deploy the environment, you need to set an environment variable for STACK_NAME. Example: `export STACK_NAME=testing-sla`
2. Next, change the directory to `cdk` as the root. 
3. Run `cdk synth --output ./`. This will give you the CloudFormation template for the stacks. Feel free to review.
4. Deploy the environment by running: `cdk deploy`. You will be prompted to approve the deploy for each stack.
5. That's it. Once deployed, you can review the cloudwatch logs for your Lambda functions to see how things are progressing. 
6. Whoever you added as a subscriber to the email notification list will get an email from SNS to approve the subscription.

Testing
-------

1. Coming soon...

Development
-----------

If you want to work on this application we’d love your pull requests and tickets on GitHub!

1. If you open up a ticket, please make sure it describes the problem or feature request fully.
2. If you send us a pull request, make sure you add a test for what you added.

Deploy to AWS
----------------

Click the button below to deploy via CloudFormation: (NOT FUNCTIONAL)

[![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=buildkite&templateURL=https://s3.amazonaws.com/the-cf-stack-here)
