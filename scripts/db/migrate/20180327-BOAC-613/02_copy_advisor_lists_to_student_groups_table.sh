#!/bin/bash

# -------------------------------------------------------------------
#
# Script must be run with sudo
#
# -------------------------------------------------------------------

# Abort immediately if a command fails
set -e

# Load environment variables
source /opt/python/current/env && env

# Run Python script
cd /opt/python/current/app
python3 scripts/db/migrate/20180327-BOAC-613/copy_advisor_lists_to_student_groups_table.py

exit 0
