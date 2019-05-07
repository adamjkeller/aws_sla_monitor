#!/usr/bin/env python3

from aws_cdk import cdk
from cdk_testing.aws_sla_monitor import AWSSlaMonitor

app = cdk.App()
AWSSlaMonitor(app, "aws-sla-monitor-cdk")

app.run()
