#!/bin/bash

sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/tmp/amazon-cloudwatch-agent.json -s
