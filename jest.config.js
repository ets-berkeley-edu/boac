module.exports = {
  moduleFileExtensions: ['js', 'json', 'ts'],
  transform: {
    '^.+\\.js$': '<rootDir>/node_modules/babel-jest',
    '.*\\.(vue)$': '<rootDir>/node_modules/vue-jest'
  },
  transformIgnorePatterns: ['<rootDir>/node_modules/'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  resolver: null,
  snapshotSerializers: ['jest-serializer-vue'],
  testMatch: [
    '**/tests-vue/**/*.spec.(js|ts|tsx)'
  ],
  testURL: 'http://localhost:8080/',
  verbose: true
};
