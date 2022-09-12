import { withVuetify } from '@socheatsok78/storybook-addon-vuetify/dist/decorators'
import store from '../src/store'

export const decorators = [
  withVuetify,
  () => ({ 
    template: "<story />",
    store 
  })
]

export const parameters = {
  actions: { argTypesRegex: "^on[A-Z].*" },
  controls: {
    matchers: {
      color: /(background|color)$/i,
      date: /Date$/,
    },
  },
}
