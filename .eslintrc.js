module.exports = {
  root: true,
  env: {
    browser: true,
    node: true
  },
  extends: [
    '@vue/typescript',
    'plugin:vue/recommended',
    'eslint:recommended',
    'plugin:vue-a11y/recommended'
  ],
  plugins: [
    'vue',
    'vue-a11y'
  ],
  rules: {
    'eqeqeq': 2,
    'multiline-html-element-content-newline': 0,
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-unexpected-multiline': 2,
    'quotes': [1, 'single'],
    'vue-a11y/label-has-for': [
      2,
      {
        'components': [ 'label' ],
        'required': {
            'every': [ 'id' ]
        },
        'allowChildren': false
      }
    ],
    'vue-a11y/no-onchange': 'off',
    'vue/array-bracket-spacing': 2,
    'vue/arrow-spacing': 2,
    'vue/attributes-order': 2,
    'vue/block-spacing': 2,
    'vue/brace-style': 2,
    'vue/camelcase': 2,
    'vue/comma-dangle': 2,
    'vue/component-name-in-template-casing': 2,
    'vue/eqeqeq': 2,
    'vue/html-closing-bracket-newline': 0,
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
    'vue/no-boolean-default': 1,
    'vue/no-restricted-syntax': 2,
    'vue/no-use-v-if-with-v-for': 2,
    'vue/no-v-html': 0,
    'vue/object-curly-spacing': 2,
    'vue/require-default-prop': 1,
    'vue/require-direct-export': 2,
    'vue/require-prop-types': 2,
    'vue/script-indent': 2,
    'vue/singleline-html-element-content-newline': 0,
    'vue/space-infix-ops': 2,
    'vue/space-unary-ops': 2,
    'vue/v-bind-style': 2,
    'vue/v-on-function-call': 1,
    'vue/v-on-style': 2
  },
  parserOptions: {
    parser: require.resolve('@typescript-eslint/parser')
  }
};
