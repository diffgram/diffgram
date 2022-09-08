import { defineConfig } from 'cypress'

export default defineConfig({
  projectId: 'djxpvm',
  viewportWidth: 1200,
  viewportHeight: 900,
  pageLoadTimeout: 180000,
  screenshotOnRunFailure: false,
  video: false,
  retries: {
    runMode: 5,
    openMode: 0,
  },
  e2e: {
    // We've imported your old cypress plugins here.
    // You may want to clean this up later by importing these.
    setupNodeEvents(on, config) {
      return require('./cypress/plugins/index.js')(on, config)
    },
  },
})
