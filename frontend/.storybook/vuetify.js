import Vue from 'vue';
import Vuetify from 'vuetify';
import theme from './theme';

Vue.use(Vuetify);

export default new Vuetify({
  theme: {
    themes: {
      light: theme,
    },
  },
});