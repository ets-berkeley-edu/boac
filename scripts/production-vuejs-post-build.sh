#!/bin/sh

# Abort immediately if a command fails
set -e

cp dist/static/vue/css/* dist/static/css/
cp dist/static/vue/js/* dist/static/js/
cp dist/static/vue/img/* dist/static/img/
cp dist/static/vue/index.html dist/static/

exit 0
