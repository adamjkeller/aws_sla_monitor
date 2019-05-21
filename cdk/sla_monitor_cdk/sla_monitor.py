#!/usr/bin/env python3

from aws_cdk import cdk
from .aws_sla_monitor import AWSSlaMonitor
from .sla_updates import AWSSlaStreamMonitor


class AWSSLAMonitorStack(cdk.Stack):

    def __init__(self, app: cdk.App, id: str) -> None:
        super().__init__(app, id)

        AWSSlaMonitor(self, "SLAMonitor", self.stack_name)
    
