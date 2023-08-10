module.exports = {
  moduleDirectories: ["node_modules", "<rootDir>"],
  moduleFileExtensions: ["js", "ts", "json", "vue"],

  transform: {
    "^.+\\.js$": "babel-jest",
    ".*\\.(vue)$": "@vue/vue2-jest",
    "^.+\\.tsx?$": "ts-jest",
  },
  "testEnvironment": "jsdom",
  transformIgnorePatterns: [
    "node_modules/(?!(three"
    + "|ol"
    + "|quick-lru"
    + "|ol-ext"
    + "|yet-another-module"
    + "|wavesurfer.js"
    + ")/)",

  ],
  setupFiles: ["<rootDir>/tests/unit/index.js"],
  "modulePaths": ["<rootDir>/src"],
  roots: ["<rootDir>/tests/"],
  moduleNameMapper: {
    "\\.(css|less)$": "<rootDir>/__mocks__/styleMock.js",
    "@/(.*)": "<rootDir>/src/$1",

  },
  globals: {
    "ts-jest": {
      tsconfig: "src/tsconfig.json"
    }
  },
};

