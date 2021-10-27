import Vuex from "vuex";
import { shallowMount, createLocalVue } from "@vue/test-utils";
import annotation_core from "@/components/annotation/annotation_core.vue";

const localVue = createLocalVue();
localVue.use(Vuex);

describe("Test annotation_core", () => {
  let props;

  beforeEach(() => {
    props = {
      mocks: {
        $get_sequence_color: () => {},
        $store: {
          state: {
            annotation_state: {},
            user: {
              settings: {
                studio_box_info: {}
              }
            },
            project: {
              current: {
                project_string_id: ""
              }
            }
          },
          getters: {
            get_view_issue_mode: () => {}
          }
        }
      }
    };
  });

  it("Test if annotation_core mounted successfully", () => {
    const wrapper = shallowMount(annotation_core, props, localVue);
    console.log(wrapper);
  });
});
