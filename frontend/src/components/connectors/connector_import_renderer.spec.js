import 'babel-polyfill';
import Vuetify from 'vuetify';
import Vuex from 'vuex'
import {route_errors} from '../regular/regular_error_handling'
import connector_import_renderer from './connector_import_renderer.vue'
import {connection} from '../../store';
import { cloneDeep } from 'lodash'
// Utilities
import {
  shallowMount,
  mount,
  createLocalVue
} from '@vue/test-utils'

const localVue = createLocalVue()
localVue.use(Vuetify);
localVue.use(Vuex);

describe('connector_import_renderer.vue', () => {
  let vuetify
  let wrapper;
  let vm;


  beforeEach(() => {
    vuetify = new Vuetify({
      icons: {
        iconfont: 'mdi'
      },
      theme: {
        primary: '#2196F3'
      }
    });
    const store = new Vuex.Store({})
  })

  it('Displays the appropriate label depending on integration name.', () => {
    const mock_conn_module = {
      ...connection,
      state: {
        ...connection.state,
        connection_list: [
          {id: 1, name: 'test'}
        ]
      }
    }
    const store = new Vuex.Store({modules: {connection: cloneDeep(mock_conn_module)}})
    wrapper = mount(connector_import_renderer, {
      localVue,
      store,
      mocks: {
        $route_api_errors: route_errors
      },
      data: {
        isFetchingBuckets: false
      },
      propsData: {
        connection: {
          integration_name: 'google_gcp'
        }
      }
    });
    wrapper.vm.$store.state.connection.connection_list = [
      {
        id: 1,
        name: 'test'
      }
    ]

    let searchbar_google = wrapper.findComponent({'ref': 'google_gcp'});
    let searchbar_aws = wrapper.findComponent({'ref': 'amazon_aws'});

    expect(searchbar_google.exists()).to.equals(true);
    expect(searchbar_aws.exists()).to.equals(false);

    wrapper = shallowMount(connector_import_renderer, {
      localVue,
      store,
      mocks: {
        $route_api_errors: route_errors
      },
      data: {
        isFetchingBuckets: false
      },
      propsData: {
        connection: {
          integration_name: 'amazon_aws'
        }
      }
    })
    wrapper.vm.$store.state.connection.connection_list = [
      {
        id: 1,
        name: 'test'
      }
    ]

    searchbar_google = wrapper.findComponent({'ref': 'google_gcp'});
    searchbar_aws = wrapper.findComponent({'ref': 'amazon_aws'});
    expect(searchbar_google.exists()).to.equals(false);
    expect(searchbar_aws.exists()).to.equals(true);
  });


})
