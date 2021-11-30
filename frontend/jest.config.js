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
    "src/components/annotation/userscript/codemirror.css"
  ],
  "modulePaths": ["<rootDir>/src"],
  roots: ["<rootDir>/tests/"],
  moduleNameMapper: {
    "@/(.*)": "<rootDir>/src/$1",
  },
  globals: {
    "ts-jest": {
      tsconfig: "src/tsconfig.json"
    }
  },
};

