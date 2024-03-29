import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="aws_sla_monitor",
    version="0.0.1",

    description="CDK App to deploy SLA Monitor Environment",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"main": "sla_monitor_sdk"},
    packages=setuptools.find_packages(where="sla_monitor_cdk"),

    install_requires=[
        "aws-cdk.cdk==0.33.0",
        "aws-cdk.aws_lambda==0.33.0",
        "aws-cdk.aws_lambda_event_sources==0.33.0",
        "aws-cdk.aws_events==0.33.0",
        "aws-cdk.aws_events_targets==0.33.0",
        "aws-cdk.aws_s3==0.33.0",
        "aws-cdk.aws_s3_deployment==0.33.0",
        "aws-cdk.aws_logs==0.33.0",
        "aws-cdk.aws_dynamodb==0.33.0",
        "aws-cdk.aws_sns==0.33.0",
        "sh",
        "requests"
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
