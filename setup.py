#!/usr/bin/env python3

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aws-sla-monitor",
    version="0.0.1",
    author="Adam Keller",
    author_email="keladam@amazon.com",
    description="Monitors AWS SLA Page and scrapes the change dates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adamjkeller/aws_sla_monitor",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
)

