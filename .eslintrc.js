module.exports = {
  root: true,
  env: {
    browser: true,
    node: true
  },
  extends: [
    '@vue/typescript',
    'plugin:vue/strongly-recommended',
    'eslint:recommended'
  ],
  plugins: ['vue'],
  rules: {
    'array-bracket-spacing': 2,
    'eqeqeq': 2,
    'key-spacing': 2,
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-multi-spaces': 2,
    'no-trailing-spaces': 2,
    'no-unexpected-multiline': 2,
    'object-curly-spacing': 2,
    'quotes': [2, 'single'],
    'semi': [2, 'never'],
    'vue/arrow-spacing': 2,
    'vue/attributes-order': 2,
    'vue/block-spacing': 2,
    'vue/brace-style': 2,
    'vue/camelcase': 2,
    'vue/comma-dangle': 2,
    'vue/component-name-in-template-casing': 2,
    'vue/eqeqeq': 2,
    'vue/html-closing-bracket-newline': 2,
    'vue/html-closing-bracket-spacing': 2,
    'vue/html-end-tags': 2,
    'vue/html-indent': 2,
    'vue/html-quotes': 2,
    'vue/html-self-closing': 0,
    'vue/key-spacing': 2,
    'vue/match-component-file-name': 2,
    'vue/max-attributes-per-line': ['error', {
      singleline: 3,
      multiline: {
        max: 1,
        allowFirstLine: false
      }
    }],
    'vue/multiline-html-element-content-newline': 2,
    'vue/no-boolean-default': 2,
    'vue/no-mutating-props': 1,
    'vue/no-restricted-syntax': 2,
    'vue/no-use-v-if-with-v-for': 2,
    'vue/no-v-html': 0,
    'vue/require-default-prop': 0,
    'vue/require-direct-export': 2,
    'vue/require-prop-types': 2,
    'vue/script-indent': 2,
    'vue/singleline-html-element-content-newline': 0,
    'vue/space-infix-ops': 2,
    'vue/space-unary-ops': 2,
    'vue/this-in-template': 2,
    'vue/valid-v-slot': [
      'error',
      {
        allowModifiers: true
      }
    ],
    'vue/v-bind-style': 2,
    'vue/v-on-function-call': 2,
    'vue/v-on-style': 2,
    'vue/v-slot-style': 0
  },
  parserOptions: {
    parser: require.resolve('@typescript-eslint/parser')
  }
}
