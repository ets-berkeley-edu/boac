#!/bin/bash

# Abort immediately if a command fails
set -e

expected_total_line_count=33389

total_line_count=$(find ${PWD}/src-vue2 -name '*.*' | xargs wc -l | grep total)

if [[ "${total_line_count}" == *"${expected_total_line_count}"* ]]; then
  exit 0
else
  exit 1
fi
