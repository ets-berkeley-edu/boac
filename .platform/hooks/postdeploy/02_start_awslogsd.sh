#!/bin/bash

commands:
  01_enable_awslogsd:
    command: sudo systemctl enable awslogsd.service
  02_restart_awslogsd:
    command: sudo systemctl restart awslogsd
