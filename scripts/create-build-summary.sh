#!/bin/sh

# Abort immediately if a command fails
set -e

shortGitHash=$(echo "${CODEBUILD_RESOLVED_SOURCE_VERSION}" | cut -c1-7)

cat << EOF > "${PWD}/config/build-summary.json"
{
  "build": {
    "artifact": "${CODEBUILD_SOURCE_VERSION}",
    "gitCommit": "${shortGitHash}"
  }
}
EOF

exit 0
