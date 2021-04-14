module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:vue/base',
    'plugin:vue/recommended',
    '@vue/typescript',
  ],
  env: {
		browser: true,
    es6: true,
    mocha: true
  },
  rules: {
    'vue/prop-name-casing': 'off',

    // https://eslint.vuejs.org/rules/html-self-closing.html
    "vue/html-self-closing": ["error", {
      "html": {
        "component": "never"
      }
    }]
    // 'vue/no-deprecated-slot-attribute': 'off',
    // 'vue/no-deprecated-filter': 'off',
  }
};

