import Vue from "vue";
import Vuetify from "vuetify";
import 'babel-polyfill';
import 'jest-canvas-mock';
import main_menu from '../../src/components/main_menu/menu'
import error_multiple from '../../src/components/regular/error_multiple'

Vue.component('main_menu', main_menu)
Vue.component('v_error_multiple', error_multiple)
Vue.config.productionTip = false;
Vue.use(Vuetify);
