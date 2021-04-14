import 'babel-polyfill';
import Vuetify from 'vuetify';
import Vuex from 'vuex'
import flushPromises from 'flush-promises';
import moxios from 'moxios';
import { route_errors } from '../regular/regular_error_handling'
import cloud_storage_searchbar from './cloud_storage_searchbar.vue'
import store from '../../store';
import {
  shallowMount,
  createLocalVue
} from '@vue/test-utils'



const localVue = createLocalVue()
localVue.use(Vuetify);
localVue.use(Vuex);

describe('cloud_storage_searchbar.vue', () => {
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
    wrapper = shallowMount(cloud_storage_searchbar, {
      localVue,
      vuetify,
      store,
      mocks:{
        $route_api_errors: route_errors
      },
      data() {
        return {
          isFetchingBuckets: false
        }
      },
      propsData:{
        project_string_id: 'my-test-project',
        connection: {id: 1},
        video_split_duration: 75,
      }
    })

    vm = wrapper.vm
  });
  afterEach(() =>{
    moxios.uninstall();
  })

  it('Should have a loader when searching buckets.', () => {
    expect(wrapper.find('.skeleton-loader-autocomplete').exists()).to.equal(true);
  });

  it('Should have an import button.', async() => {
    // We need to use next tick because the initial state of the component is a loader. We have to wait until it
    // updates in order to have de button available
    await wrapper.setData({isFetchingBuckets: false});
    expect(wrapper.find('[data-cy=start-importing]').exists()).to.equal(true);
  });

  it('Should set syncstatus to loading when calling start_folder_fetch', async () => {
    moxios.stubRequest(`/api/walrus/v1/connectors/${1}/fetch-data`,{
      status: 200,
      response: {
        result: true
      }
    });
    vm.start_folder_fetch();
    expect(vm.$data.importStatus).to.equal('loading')
  });

  it('Should set syncstatus to success when calling finished for start_folder_fetch', async() => {
    moxios.stubRequest(`/api/walrus/v1/connectors/${1}/fetch-data`,{
      status: 200,
      response: {
        result: true
      }
    });
    await vm.start_folder_fetch();
    await flushPromises();
    await vm.$nextTick();
    expect(vm.$data.importStatus).to.equal('success')
  });

  it('Should empty folder_contents when calling change_bucket', () => {
    vm.change_bucket();
    expect(vm.$data.items.length).to.equal(0);

  })

  it('Should close the dialog when calling close_success_dialog', () =>{
    vm.close_success_dialog();
    expect(vm.$data.dialog).to.equal(false);
  });

  it('should update appropriate data when calling show_confirm_dialog', () =>{
    vm.show_confirm_dialog();
    expect(vm.$data.dialog).to.equal(true);
    expect(vm.$data.importStatus).to.equal('pending');
  })


  it('Should send to backend the video split duration config.', async () =>{
    moxios.stubRequest('/api/walrus/v1/connectors/1/fetch-data',{
      status: 200,
      response: {
        result: true
      }
    });
    await vm.start_folder_fetch()
    await flushPromises();
    await vm.$nextTick();
    const request_payload = JSON.parse(moxios.requests.mostRecent().config.data);
    expect(request_payload.opts.video_split_duration).to.equal(vm.$props.video_split_duration);

  })

})
