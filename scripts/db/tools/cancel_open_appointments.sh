#!/bin/bash

# -------------------------------------------------------------------
#
# Connect to BOAC RDS using credentials in local configs and run cancel_open_appointments.sql.
#
# -------------------------------------------------------------------

# Abort immediately if a command fails
set -e

echo "Starting cancel_open_appointments script."

if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root."; echo
  exit 1
fi

local_config="/opt/python/current/app/config/production-local.py"

if [ -e "${local_config}" ]; then
  db_uri=$(grep SQLALCHEMY_DATABASE_URI "${local_config}" | sed "s/^SQLALCHEMY_DATABASE_URI[ ]*=[ ]*'//" | sed "s/'[ ]*//")

  if [ -z "${db_uri}" ]; then
    echo "[ERROR] SQLALCHEMY_DATABASE_URI not found in ${local_config}."; echo
    exit 1
  fi

else
  echo "File not found: ${local_config}"; echo
  exit 1
fi

psql "${db_uri}" -f /opt/python/current/app/scripts/db/tools/cancel_open_appointments.sql

echo "Done! Have a nice day."; echo

exit 0
