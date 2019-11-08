#!/usr/bin/env bash

# Vanilla shell script (no Python needed) which requests cache refreshing for the current term
# on a BOAC application server.

# Sample config file format (all lines left-justified):
#
#   BOAC_URL="https://ets-boac.example.com"
#   BOAC_API_KEY="Regents of the University of California"

echo_usage() {
  echo; echo "USAGE"; echo "    ${0} [Path to config file]"
  echo; echo "[OPTIONAL] LOGDIR=/hither/thither/logs"
  echo
}

[[ $# -gt 0 ]] || { echo_usage; exit 1; }

if [[ -z "${LOGDIR}" ]]; then
  LOGDIR="."
fi
log_file="${LOGDIR}/boac_refresh_$(date +"%Y-%m-%d_%H%M%S").log"

CONFIG_FILE=$1

echo
echo "Log file is ${log_file}"
echo | tee -a ${log_file}
echo "Config file is ${CONFIG_FILE}" | tee -a ${log_file}

set -o allexport
source $CONFIG_FILE
set +o allexport

# Refreshes external data cache for the current term.
url="${BOAC_URL}/api/admin/cachejob/refresh"

echo | tee -a ${log_file}
echo "About to ping ${url}" | tee -a ${log_file}
echo | tee -a ${log_file}
# The more typical underscored "app_key" header will be stripped out by the AWS load balancer.
# A hyphened "app-key" header passes through.
response_metadata=$(curl -k --header "app-key: ${BOAC_API_KEY}" "${url}" 2>&1)
echo "Got response:" | tee -a ${log_file}
echo | tee -a ${log_file}
echo "${response_metadata}" | tee -a ${log_file}
echo | tee -a ${log_file}
echo "Job status can be checked at ${BOAC_URL}/api/admin/cachejob" | tee -a ${log_file}
echo "[DONE]"; echo

exit 0
