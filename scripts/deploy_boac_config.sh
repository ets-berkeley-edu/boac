#!/bin/bash

# -------------------------------------------------------------------
#
# Copy appropriate config file from S3 to production-local.py. This
# script must be run on the target EC2 instance (eg, boac-dev).
#
# -------------------------------------------------------------------

# Abort immediately if a command fails
set -e

echo; echo "Welcome!"; echo

if [ "$EUID" -ne 0 ]; then
  echo "Sorry, you must use 'sudo' to run this script."; echo
  exit 1
fi

local_config="/var/app/current/config/production-local.py"

if [ -e "${local_config}" ]; then
  eb_env=$(grep EB_ENVIRONMENT "${local_config}" | sed "s/^EB_ENVIRONMENT[ ]*=[ ]*'//" | sed "s/'[ ]*//")

  if [ -z "${eb_env}" ]; then
    echo "[ERROR] EB_ENVIRONMENT not found in ${local_config}. Please report the problem."; echo
    exit 1
  else
    echo "EB_ENVIRONMENT is '${eb_env}' according to ${local_config}"; echo
  fi

else
  echo "File not found: ${local_config}"; echo
  exit 1
fi

# Download from Amazon S3
config_location="s3://la-deploy-configs/boac/${eb_env}.py"

echo "In five seconds, ${config_location} will be copied to ${local_config}."; echo
echo "Use CTRL-C to abort..."; echo
sleep 5

AWS_REGION=us-west-2 aws s3 cp ${config_location} "${local_config}"
chown webapp "${local_config}"
chmod 400 "${local_config}"

# Add EB_ENVIRONMENT to new config file
printf "\nEB_ENVIRONMENT = '${eb_env}'\n\n" >> "${local_config}"

echo; echo "Done!"; echo
echo "Restart BOA to pick up new configs. Have a nice day!"; echo

exit 0
