import 'babel-polyfill';
import Vuetify from 'vuetify';
import Vuex from 'vuex'
import flushPromises from 'flush-promises';
import { route_errors } from '../regular/regular_error_handling'
import moxios from 'moxios';
import export_storage_searchbar from './export_storage_searchbar.vue'
import store from '../../store';
import {
  shallowMount,
  createLocalVue
} from '@vue/test-utils'



const localVue = createLocalVue()
localVue.use(Vuetify);
localVue.use(Vuex);

describe('export_storage_searchbar.vue', () => {
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
    moxios.install();
    wrapper = shallowMount(export_storage_searchbar, {
      localVue,
      vuetify,
      store,
      mocks:{
        $route_api_errors: route_errors
      },
      data(){
        return {
          isFetchingBuckets: false,
          selection: [{id:88}]
        }
      },
      propsData:{
        project_string_id: 'my-test-project',
        export_obj: {
          id: 5484848
        },
        connection:{
          id: 1
        }
      }
    })

    vm = wrapper.vm
  })

  it('Should have a tree view component.', () => {
    expect(wrapper.find('.skeleton-loader-autocomplete').exists()).to.equal(true);
  });


  it('Should empty folder_contents when calling change_bucket', () => {
    vm.change_bucket();
    expect(vm.$data.items.length).to.equal(0);

  })

  it('Should stop loading state when do_folder_search completes', async () =>{
    moxios.stubRequest(`/api/walrus/v1/connectors/1/put-data`,{
      status: 200,
      response: {
        data:{
          result: true
        }
      }
    });
    await vm.start_export()
    await flushPromises();
    await vm.$nextTick();
    expect(vm.$data.exportStatus).to.equal('success');

  })
})
