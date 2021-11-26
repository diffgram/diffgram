module.exports = {
  preset: "@vue/cli-plugin-unit-jest/presets/no-babel",
  moduleFileExtensions: ["js", "ts", "json", "vue"],
  transform: {
    ".*\\.(vue)$": "vue-jest",
    "^.+\\.tsx?$": "ts-jest"
  },
  "modulePaths": ["<rootDir>/src"],
  globals: {
    "ts-jest": {
      tsconfig: "src/tsconfig.json"
    }
  }
};
