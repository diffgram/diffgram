import {shallowMount, createLocalVue} from "@vue/test-utils";
import Vuex from 'vuex'
import axios from '../../../../../src/services/customInstance'
import step_name_task_template
  from "../../../../../src/components/task/job/task_template_wizard_creation/step_name_task_template";
import VueRouter from 'vue-router'

const localVue = createLocalVue();
localVue.use(Vuex)
localVue.use(VueRouter)
const router = new VueRouter()

let job = {
  name: '',
  label_mode: 'closed_all_available',

  loading: false,
  passes_per_file: 1,
  share_object: {
    // TODO this may fail for org jobs? double check this.
    'text': String,
    'type': 'project'
  },
  share: 'project',
  instance_type: 'box', //"box" or "polygon" or... "text"...
  permission: 'all_secure_users',
  field: 'Other',
  category: 'visual',
  attached_directories_dict: {attached_directories_list: []},
  type: 'Normal',
  connector_data: {},
  // default to no review while improving review system
  review_by_human_freqeuncy: 'No review', //'every_3rd_pass'
  td_api_trainer_basic_training: false,
  file_handling: "use_existing",
  interface_connection: undefined,
  member_list_ids: ["all"]
}
describe("step_name_task_template.vue", () => {
  let actions;
  let store;

  beforeEach(() => {
    actions = {
      actionClick: jest.fn(),
      actionInput: jest.fn()
    }
    store = new Vuex.Store({
      actions
    })
  });


  it("Renders component correctly.", () => {
    const wrapper = shallowMount(step_name_task_template, {
      store,
      localVue,
      propsData: {
        job: job
      }
    });
    expect(wrapper).toMatchSnapshot();
  });

  it("Populates error data when calling verify_name().", () => {
    const wrapper = shallowMount(step_name_task_template, {
      store,
      localVue,
      propsData: {
        job: job
      }
    });
    wrapper.vm.verify_name();
    expect(wrapper.vm.error).toMatchObject({
      name: 'Name must not be empty.'
    })
  });

  it("Emits event when calling on_next_button_click()", async () => {
    const wrapper = shallowMount(step_name_task_template, {
      store,
      localVue,
      propsData: {
        job: {
          ...job,
          id: 5,
          name: 'test'
        }
      }
    });
    await wrapper.vm.on_next_button_click()
    expect(wrapper.emitted().next_step.length).toBe(1);
  });

  it("Makes request to /job/new when calling job_new()", () => {
    jest.mock('axios', () => ({
      post: jest.fn(() => {})
    }))
    const wrapper = shallowMount(step_name_task_template, {
      store,
      localVue,
      propsData: {
        job: job,
        project_string_id: 'test'
      }
    });
    let url = `/api/v1/project/test/job/new`;
    const spy = jest.spyOn(axios, 'post')
    wrapper.vm.job_new()
    expect(spy).toHaveBeenCalledWith(url, job);
  });



});
