#!/bin/bash

commands:
  01_enable_awslogsd:
    command: systemctl enable awslogsd.service
  02_restart_awslogsd:
    command: systemctl restart awslogsd
