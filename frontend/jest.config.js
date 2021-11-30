module.exports = {
  moduleFileExtensions: ["js", "ts", "json", "vue"],
  transform: {
    "^.+\\.js$": "babel-jest",
    ".*\\.(vue)$": "vue-jest",
    "^.+\\.tsx?$": "ts-jest",
  },
  transformIgnorePatterns: [
    "node_modules/(?!(three"
    + "|another-module"
    + "|yet-another-module"
    + ")/)",

  ],
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

