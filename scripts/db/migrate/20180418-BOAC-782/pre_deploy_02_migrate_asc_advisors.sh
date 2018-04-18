#!/bin/bash

# -------------------------------------------------------------------
#
# Script must be run with sudo
#
# -------------------------------------------------------------------

# Abort immediately if a command fails
set -e

# Load env variables
[ -e /opt/python/current/env ] && source /opt/python/current/env && env

[ -d /opt/python/current/app ] && cd /opt/python/current/app

# Run Python script
python3 scripts/db/migrate/20180418-BOAC-782/pre_deploy_02_migrate_asc_advisors.py

echo 'Done.'

exit 0
