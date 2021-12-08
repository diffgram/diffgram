import Vuex from "vuex";
import Vuetify from "vuetify";
import { shallowMount, createLocalVue } from "@vue/test-utils";
import annotation_core from "@/components/annotation/annotation_core.vue";
const vuetify = new Vuetify();
const localVue = createLocalVue();
localVue.use(Vuex);

describe("Test annotation_core", () => {
  let props;

  beforeEach(() => {
    props = {
      mocks: {
        $get_sequence_color: () => {},
        task: 1,
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
        },

      },
      vuetify
    };
  });

  it("Tests if annotation_core mounts successfully", () => {
    const wrapper = shallowMount(annotation_core, props, localVue);
    expect(wrapper.html().includes('id="annotation_core"')).toBeTruthy();
  });
});
