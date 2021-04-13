import 'babel-polyfill';
import Vuetify from 'vuetify';
import Vuex from 'vuex'
import flushPromises from 'flush-promises';
import { route_errors } from '../regular/regular_error_handling'
import export_connection_dialog from './export_connection_dialog.vue'
import connection_select from '../connection/connection_select.vue'
import connector_export_renderer from './connector_export_renderer.vue'
import store from '../../store';

// Utilities
import {
  shallowMount,
  createLocalVue
} from '@vue/test-utils'

const localVue = createLocalVue()
localVue.use(Vuetify);
localVue.use(Vuex);

describe('export_connection_dialog.vue', () => {
  let vuetify
  let wrapper;
  let vm;


  beforeEach(() => {
    vuetify = new Vuetify({
      icons : {
        iconfont: 'mdi'
      },
      theme: {
        primary: '#2196F3'
      }
    });
  })

  wrapper = shallowMount(export_connection_dialog, {
    localVue,
    mocks:{
      $route_api_errors: route_errors
    },
    data:{
      isFetchingBuckets: false
    },
    propsData:{
      connection:{
        integration_name: 'google_gcp'
      }
    }
  })

  it('Displays the appropriate label depending on integration name.', () => {
      expect(wrapper.find('#export-dialog').exists()).to.equals(true);
  });


  it('Displays the connection select.', () => {
    expect(wrapper.findAllComponents(connection_select).exists()).to.equals(true);
  });


  it('Displays the connection export renderer.', () => {
    expect(wrapper.findAllComponents(connector_export_renderer).exists()).to.equals(true);
  });



})
