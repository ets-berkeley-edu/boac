#!/bin/bash

# -------------------------------------------------------------------
#
# Script must be run with sudo
#
# -------------------------------------------------------------------

# Abort immediately if a command fails
set -e

if [ "$EUID" -ne 0 ]; then
  echo "Sorry, you must use 'sudo' to run this script."; echo
  exit 1
fi

# Load env variables
[ -e /opt/python/current/env ] && source /opt/python/current/env && env

# Run Python script
cd /opt/python/current/app
python3 scripts/db/migrate/20190924-BOAC-2620/post_deploy_01_gpa_json_in_cohort_filter.py

echo 'Done.'

exit 0
