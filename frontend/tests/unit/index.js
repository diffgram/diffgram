import Vue from "vue";
import Vuetify from "vuetify";
import 'babel-polyfill';
import 'jest-canvas-mock';

import main_menu from '../../src/components/main_menu/menu'

Vue.component('main_menu', main_menu)

Vue.config.productionTip = false;
Vue.use(Vuetify);
