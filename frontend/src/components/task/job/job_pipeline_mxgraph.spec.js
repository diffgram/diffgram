import 'babel-polyfill';
import Vuetify from 'vuetify';
import Vuex from 'vuex'
import flushPromises from 'flush-promises';
import moxios from 'moxios';
import {route_errors} from '../../regular/regular_error_handling'
import job_pipeline_mxgraph from './job_pipeline_mxgraph.vue'
import store, {project, user_module} from '../../../store';
import {cloneDeep} from 'lodash'
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
      icons: {
        iconfont: 'mdi'
      },
      theme: {
        primary: '#2196F3'
      }
    });
    moxios.install();
    const mock_project = {
      ...project,
      state: {
        ...project.state,
        project_name: 'test',
        project_string_id: 'test',

        current_directory: {id: 1},
        current: {
          project_string_id: 'test',
        }
      }
    }
    const mock_user = {
      ...user_module,
      state: {
        ...user_module.state,
        current: {
          trainer: {},
          api: {},
          email: null,
          username: 'test'
        },
      }
    }
    const store = new Vuex.Store({
      modules: {
        project: cloneDeep(mock_project),
        user: cloneDeep(mock_user)
      }
    })
    const mock_response = {
      job: {
        id: 234,
        name: 'my new job',
        attached_directories_dict: {
          attached_directories_list: []
        },
        completion_directory_id: 1
      },
      log: {}
    };
    const url = `/api/v1/job/5/builder/info`
    const url_dir = `/api/project/test/user/test/working_dir/view`
    moxios.stubRequest(url, {
      status: 200,
      responseText: mock_response
    })
    moxios.stubRequest(url_dir, {
      status: 200,
      responseText: {working_dir: {directory_id: 1, nickname: 'dirtest'}, success: true}
    });
    wrapper = shallowMount(job_pipeline_mxgraph, {
      localVue,
      vuetify,
      store,
      mocks: {},
      data() {
        return {}
      },
      propsData: {
        job_id: 5

      }
    })
  });
  afterEach(() => {
    moxios.uninstall();
  })

  it('Should have an MxGraph container.', () => {
    expect(wrapper.find('[data-cy=mxgraphcontainer]').exists()).to.equal(true);
  });

  it('Should populate job data when calling fetch_job()', (done) => {
    const mock_response = {
      job: {
        id: 234,
        name: 'my new job',
        attached_directories_dict: {
          attached_directories_list: []
        },
        completion_directory_id: 1
      },
      log: {}
    };
    wrapper.vm.fetch_job().then(() => {
      expect(wrapper.vm.$data.job.id).to.equal(mock_response.job.id);
      done();
    });

    flushPromises();

  });
})
