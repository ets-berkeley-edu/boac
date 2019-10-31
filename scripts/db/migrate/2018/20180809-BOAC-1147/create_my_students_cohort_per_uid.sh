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
advisor_uid=${1}
advisor_first_name="${2}"

cd /opt/python/current/app
python3 scripts/db/migrate/20180809-BOAC-1147/create_my_students_cohort_per_uid.py "${advisor_uid}" "${advisor_first_name}"

echo 'Done.'

exit 0
