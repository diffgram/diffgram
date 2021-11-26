import Vuex from "vuex";
import { shallowMount, createLocalVue } from "@vue/test-utils";
import canvas_3d from "../../../src/components/3d_annotation/canvas_3d.vue";

const localVue = createLocalVue();
localVue.use(Vuex);

describe("Test canvas_3d.vue", () => {
  let props;

  beforeEach(() => {
    props = {
      container_id: 'test_canvas_3d',
      mocks: {
        $get_sequence_color: () => {},
        file: {
          id: 1,
          type: 'sensor_fusion',

        },
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

  it("Tests if canvas_3d mounts successfully", () => {
    const wrapper = shallowMount(canvas_3d, props);
    expect(wrapper.html().includes(`id="${props.container_id}"`)).toBeTruthy();
  });
});
