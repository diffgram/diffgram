import {shallowMount, createLocalVue} from "@vue/test-utils";
import Vuex from 'vuex'
import axios from 'axios'
import step_label_selection_task_template
  from "../../../../../src/components/task/job/task_template_wizard_creation/step_label_selection_task_template";
import VueRouter from 'vue-router'
import step_guides_task_template
  from "../../../../../src/components/task/job/task_template_wizard_creation/step_guides_task_template";
const localVue = createLocalVue();
localVue.use(Vuex)
localVue.use(VueRouter)
const router = new VueRouter()

let job = {
  name: 'test',
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
describe("step_label_selection_task_template.vue", () => {
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
    const wrapper = shallowMount(step_label_selection_task_template, {
      store,
      localVue,
      propsData: {
        job: job
      }
    });
    expect(wrapper).toMatchSnapshot();
  });

  it("Sets error data when calling verify_labels()", () => {
    const wrapper = shallowMount(step_label_selection_task_template, {
      store,
      localVue,
      propsData: {
        job: job
      }
    });
    wrapper.vm.verify_labels()
    expect(wrapper.vm.error).toMatchObject({
      name: 'At least 1 user should be assigned to the task template.'
    })
  });


  it("It sets label file list when calling on_change_label_file()", () => {
    const wrapper = shallowMount(step_label_selection_task_template, {
      store,
      localVue,
      propsData: {
        job: job
      }
    });
    wrapper.vm.on_change_label_file('test')
    expect(wrapper.vm.job.label_file_list).toEqual('test');
  });



});
