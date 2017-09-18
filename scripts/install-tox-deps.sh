#!/bin/bash

# Fail the entire script when one of the commands in it fails
set -e

hash eslint 2>/dev/null || npm install --save-dev --silent -g eslint

hash stylelint 2>/dev/null || \
  (
    npm install --save-dev --silent -g stylelint && \
    npm install --save-dev --silent stylelint-config-standard stylelint-order stylelint-scss debug
  )

exit 0
