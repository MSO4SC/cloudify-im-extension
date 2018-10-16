#!/bin/bash

cfy blueprints validate blueprint.yaml
cfy init --install-plugins -b test blueprint.yaml
cfy init blueprint.yaml
cfy -vvv executions start -b test install
#cfy executions start -b test run_jobs
cfy -vvv executions start -b test uninstall

