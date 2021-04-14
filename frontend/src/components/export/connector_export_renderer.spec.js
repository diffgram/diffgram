import 'babel-polyfill';
import Vuetify from 'vuetify';
import Vuex from 'vuex'
import { route_errors } from '../regular/regular_error_handling'
import connector_export_renderer from './connector_export_renderer.vue'

// Utilities
import {
  shallowMount,
  createLocalVue
} from '@vue/test-utils'

const localVue = createLocalVue()
localVue.use(Vuetify);
localVue.use(Vuex);

describe('connector_export_renderer.vue', () => {
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

  it('Displays the appropriate label depending on integration name.', () => {

    wrapper = shallowMount(connector_export_renderer, {
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
    let searchbar_google = wrapper.findComponent({'ref': 'google_gcp'});
    let searchbar_aws = wrapper.findComponent({'ref': 'amazon_aws'});
    expect(searchbar_google.exists()).to.equals(true);
    expect(searchbar_aws.exists()).to.equals(false);

    wrapper = shallowMount(connector_export_renderer, {
      localVue,
      mocks:{
        $route_api_errors: route_errors
      },
      data:{
        isFetchingBuckets: false
      },
      propsData:{
        connection:{
          integration_name: 'amazon_aws'
        }
      }
    })
    searchbar_google = wrapper.findComponent({'ref': 'google_gcp'});
    searchbar_aws = wrapper.findComponent({'ref': 'amazon_aws'});
    expect(searchbar_google.exists()).to.equals(false);
    expect(searchbar_aws.exists()).to.equals(true);
  });




})
