#!/bin/sh

# Abort immediately if a command fails
set -e

# The following update of .env.local is necessary because Google Analytics is loaded in our index.html file, beyond
# the scope of the Vue.js initialization context.
cat << EOF > "${PWD}/.env.local"
VUE_APP_GOOGLE_ANALYTICS_ID='${GOOGLE_ANALYTICS_ID}'
EOF

chmod 400 .env.local

exit 0
