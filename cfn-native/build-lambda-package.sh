#!/usr/bin/env bash

python3=$(which python3)

# Setup and use virtualenv to isolate packages to build
virtualenv --python=python3 venv
source venv/bin/activate

# Install packages and exit virtual environment
pip install -r ../requirements.txt
deactivate

# Package and compress python dependencies and lambda code
cwd=$(pwd)
pushd venv/lib/python3*/site-packages/
zip -r9 $cwd/slamonitor-lambda-code.zip .
popd
zip -g -j slamonitor-lambda-code.zip ../src/*

