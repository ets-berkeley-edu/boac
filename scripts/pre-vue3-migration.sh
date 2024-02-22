#!/usr/bin/env bash

git mv src src-vue2

git mv .browserslistrc vue2.browserslistrc
git mv babel.config.js vue2.babel.config.js
git mv package.json vue2.package.json
git mv postcss.config.js vue2.postcss.config.js
git mv tsconfig.json vue2.tsconfig.json
git mv vue.config.js vue2.vue.config.js

exit 0
