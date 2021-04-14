import 'babel-polyfill';
import Vuetify from 'vuetify';
import Vuex from 'vuex'
import flushPromises from 'flush-promises';
import moxios from 'moxios';
import { route_errors } from '../../regular/regular_error_handling'
import job_new_form from './job_new_form.vue'
import store from '../../../store';
import {
  shallowMount,
  createLocalVue
} from '@vue/test-utils'



const localVue = createLocalVue()
localVue.use(Vuetify);
localVue.use(Vuex);

describe('job_new_form.vue', () => {
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
    wrapper = shallowMount(job_new_form, {
      localVue,
      vuetify,
      store,
      mocks:{

      },
      data() {
        return {

        }
      },
      propsData:{
        job: {
          name: 'mytesstjob',
          label_mode: 'closed_all_available',
          passes_per_file: 1,
          share_object: {
            // TODO this may fail for org jobs? double check this.
            'text': String,
            'type': 'project'
          },
          share:  'project',
          instance_type: 'box', //"box" or "polygon" or... "text"...
          permission: 'all_secure_users',
          field: 'Other',
          category: 'visual',
          type: 'Normal',
          connector_data: {},
          // default to no review while improving review system
          review_by_human_freqeuncy: 'No review', //'every_3rd_pass'
          td_api_trainer_basic_training: false,
          file_handling: "use_existing"
        },
        project_string_id: 'test',
      }
    })
  });
  afterEach(() =>{
    moxios.uninstall();
  })

  it('Should have a text input.', () => {
    expect(wrapper.find('[data-cy=name-input]').exists()).to.equal(true);
  });
  it('Should have an Instance Type Select Field.', () => {
    expect(wrapper.find('[data-cy=instance-type-select]').exists()).to.equal(true);
  });
  it('Should have a Share Select Field.', () => {
    expect(wrapper.find('[data-cy=share-select]').exists()).to.equal(true);
  });
  it('Should have a Type Select Field.', () => {
    expect(wrapper.find('[data-cy=type-select]').exists()).to.equal(true);
  });
  it('Should have a Label Field.', () => {
    expect(wrapper.find('[data-cy=label-select]').exists()).to.equal(true);
  });
  it('Should have a Type File Handling Field.', () => {
    expect(wrapper.find('[data-cy=file-handling-select]').exists()).to.equal(true);
  });
  it('Should have an Error handler component.', () => {
    expect(wrapper.find('[data-cy=error-handler]').exists()).to.equal(true);
  });
  it('Should have a create job button.', () => {
    expect(wrapper.find('[data-cy=create-job-button]').exists()).to.equal(true);
  });
  it('Should have an update job button when job_id is not null.', () => {
    wrapper = shallowMount(job_new_form, {
      localVue,
      vuetify,
      store,
      mocks:{

      },
      data() {
        return {

        }
      },
      propsData:{
        job: {
          name: 'mytesstjob',
          label_mode: 'closed_all_available',
          passes_per_file: 1,
          share_object: {
            // TODO this may fail for org jobs? double check this.
            'text': String,
            'type': 'project'
          },
          share:  'project',
          instance_type: 'box', //"box" or "polygon" or... "text"...
          permission: 'all_secure_users',
          field: 'Other',
          category: 'visual',
          type: 'Normal',
          connector_data: {},
          //  default to no review while improving review system
          review_by_human_freqeuncy: 'No review', //'every_3rd_pass'
          td_api_trainer_basic_training: false,
          file_handling: "use_existing"
        },
        job_id: 56
      }
    })
    expect(wrapper.find('[data-cy=update-job-button]').exists()).to.equal(true);
  });
  it('Should update job.label_file_list when calling receive_file_label()', () => {
    const test_file_list = ['test1', 'test2']
    wrapper.vm.receive_label_file(test_file_list);
    expect(wrapper.vm.$props.job.label_file_list).to.equal(test_file_list);
  });
  it('Should emit job-updated event when calling job_update()', async () => {
    const mock_response = {
      job:{
        id: 234,
        name: 'my new job'
      },
      log:{
        success:true
      }
    };
    const url = `/api/v1/project/${wrapper.vm.$props.project_string_id}/job/update`;
    moxios.stubRequest(url, {
      status: 200,
      responseText: mock_response
    })
    await wrapper.vm.job_update();
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted()['job-updated'].length).to.equal(1)
  });

  it('Should emit job-created event when calling job_new() and request succeeding', async () => {
    const mock_response = {
      job:{
        id: 234,
        name: 'my new job'
      },
      log:{
        success:true
      }
    };
    const url = `/api/v1/project/${wrapper.vm.$props.project_string_id}/job/new`;
    moxios.stubRequest(url, {
      status: 200,
      responseText: mock_response
    })
    await wrapper.vm.job_new()
    expect(wrapper.emitted()['job-created'].length).to.equal(1)

  });

  it('Should make a request with job data when calling job_new()', async () => {
    const mock_response = {
      job:{
        id: 234,
        name: 'my new job'
      },
      log:{
        success:true
      }
    };
    const url = `/api/v1/project/${wrapper.vm.$props.project_string_id}/job/new`;
    moxios.stubRequest(url, {
      status: 200,
      responseText: mock_response
    })
    await wrapper.vm.job_new()
    let request = moxios.requests.mostRecent();
    expect(request.config.url).to.equal(url);
    expect(request.config.method).to.equal('post');
    expect(request.config.data).to.equal(JSON.stringify(wrapper.vm.$props.job));

  });
  it('Should populate job_new_error when calling job_new() and failing', async () => {
    const mock_response = {
      job:{
        id: 234,
        name: 'my new job'
      },
      log:{
        error: {
          test: 'test'
        }
      }
    };
    const url = `/api/v1/project/${wrapper.vm.$props.project_string_id}/job/new`;
    moxios.stubRequest(url, {
      status: 400,
      responseText: mock_response
    })
    await wrapper.vm.job_new()
    expect(wrapper.vm.$data.job_new_error).to.equal(mock_response.log.error);

  });
})
