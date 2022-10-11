const path = require('path')

function resolve(dir) {
  return path.join(__dirname, dir)
}

module.exports = {
  stories: ["../src/**/*.stories.mdx", "../src/**/*.stories.@(js|jsx|ts|tsx)"],
  addons: [
    "@storybook/addon-links",
    "@storybook/addon-essentials",
    "@storybook/addon-interactions",
    "@storybook/theming",
  ],
  framework: "@storybook/vue",
  webpackFinal: async (config) => {
    config.resolve.alias['@'] = path.resolve(__dirname, '../src/');
    return config;
  },
};
