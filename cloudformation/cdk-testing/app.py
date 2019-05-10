#!/usr/bin/env python3

from aws_cdk import cdk
from cdk_testing.sla_monitor import AWSSLAMonitorStack

app = cdk.App()

# Create the monitor stack
AWSSLAMonitorStack(app, "keladam")

app.run()
