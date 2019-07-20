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
python3 scripts/db/migrate/20190716-BOAC-2256/alter_urm_key_in_cohort_json.py

echo 'Done.'

exit 0
