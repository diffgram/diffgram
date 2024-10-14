/// <reference types="cypress" />

// This function is called when a project is opened or re-opened (e.g. due to
// the project's config changing)

/**
 * @type {Cypress.PluginConfig}
 */
const browserify = require('@cypress/browserify-preprocessor');

module.exports = (on) => {
  const options = browserify.defaultOptions;
  options.browserifyOptions.transform[1][1].babelrc = true;
  options.browserifyOptions.transform[1][1].retainLines = true;

  on('file:preprocessor', browserify(options));
};

module.exports.options = {
  viewportWidth: 1920,
  viewportHeight: 1080,
  defaultCommandTimeout: 10000,
};
