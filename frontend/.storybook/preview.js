import vuetify from './vuetify';
import { withVuetify } from '@socheatsok78/storybook-addon-vuetify/dist/decorators';
import '!style-loader!css-loader!sass-loader!./main.scss';

import Vue from 'vue';

export const parameters = {
  actions: { argTypesRegex: '^on[A-Z].*' },
  controls: {
    matchers: {
      color: /(background|color)$/i,
      date: /Date$/,
    },
  },
};

export const decorators = [
  (story, context) => {
    const wrapped = story(context);

    return Vue.extend({
      vuetify,
      components: { wrapped },
      template: `
        <v-app>
          <v-container fluid>
            <wrapped/>
          </v-container>
        </v-app>
    `,
    });
  },
  withVuetify,
];