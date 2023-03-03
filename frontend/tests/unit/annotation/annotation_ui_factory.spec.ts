import Vuex from "vuex";
import Vuetify from "vuetify";
import {shallowMount, createLocalVue} from "@vue/test-utils";
import annotation_ui_factory from "../../../src/components/annotation/annotation_ui_factory.vue";
import VueRouter from 'vue-router'
const vuetify = new Vuetify();
const localVue = createLocalVue();
import '@/vue-canvas.js'

localVue.use(Vuex);
localVue.use(VueRouter)
describe("Test annotation_ui_factory.vue", () => {
  let props;

  beforeEach(() => {
    props = {
      propsData:{
        label_schema:{
          id: 1,
          name: 'test'
        },
        task_error: {},
        image_annotation_ctx: {
          label_settings: {},
        },
        issues_ui_manager: {},
        annotation_ui_context: {
          current_image_annotation_ctx: {},
          working_file: {
            id: 1
          },
          working_file_list: [
            {
              id: 1
            }
          ]
        },
        global_attribute_groups_list: [],
        working_file: {
          id: 1
        }
      },
      mocks: {
        $get_sequence_color: () => {
        },
        $route:{

        },
        task: 1,
        label_schema:{
          id: 1,
          name: 'test'
        },
        global_attribute_groups_list: [],
        $store: {
          state: {
            annotation_state: {},
            builder_or_trainer: {
              mode: 'builder'
            },
            user: {
              settings: {
                studio_box_info: {}
              }
            },
            clipboard: {
              clipboard_data: {instance_list: [{x: 1}, {x: 2}]}
            },
            project: {
              current_directory: {
                directory_id: -1
              },
              current: {
                project_string_id: "",

              }
            }
          },
          getters: {
            get_view_issue_mode: () => {
            },
            get_clipboard: {
              instance_list: [{x: 1}, {x: 2}]
            }
          },
          mutations: {
            set_clipboard(state, data) {
              state.clipboard_data = data
            },
            clear_clipboard(state) {
              state.clipboard_data = undefined;
            }
          }
        },

      },
      vuetify
    };
  });

  it("Tests if annotation_core mounts successfully", () => {
    const wrapper = shallowMount(annotation_ui_factory, props);
    expect(wrapper.html().includes('id="annotation_factory_container"')).toBeTruthy();
  });



});
