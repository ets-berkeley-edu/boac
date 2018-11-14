module.exports = {
  root: true,
  env: {
    browser: true,
    jest: true,
    node: true
  },
  extends: [
    '@vue/prettier',
    '@vue/typescript',
    'eslint:recommended',
    'plugin:vue/essential'
  ],
  plugins: ['vue', 'prettier'],
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'prettier/prettier': [
      'error',
      {
        singleQuote: true
      }
    ]
  },
  parserOptions: {
    parser: 'typescript-eslint-parser'
  }
};
