import Vuex from "vuex";
import Vuetify from "vuetify";
import { shallowMount, createLocalVue } from "@vue/test-utils";
import annotation_core from "@/components/annotation/annotation_core.vue";
const vuetify = new Vuetify();
const localVue = createLocalVue();
import '@/vue-canvas.js'
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

  it("Tests if any_frame_saving returns correct value", () => {
    const wrapper = shallowMount(annotation_core, props, localVue);
    let result = wrapper.vm.any_frame_saving;

    expect(result).toBe(false)

    wrapper.setData({
      save_loading_frames_list: [1,2,3]
    })
    let result2 = wrapper.vm.any_frame_saving;

    expect(result2).toBe(true)
  });

  it("Tests if has_pending_frames returns correct value", () => {
    const wrapper = shallowMount(annotation_core, props, localVue);
    let result = wrapper.vm.has_pending_frames;

    expect(result).toBe(false)

    wrapper.setData({
      unsaved_frames: [1,2,3]
    })
    let result2 = wrapper.vm.has_pending_frames;

    expect(result2).toBe(true)
  });

  it("Tests correctly calls get_save_loading", () => {
    const wrapper = shallowMount(annotation_core, props, localVue);

    // Image Case
    let result = wrapper.vm.get_save_loading();
    expect(result).toBe(false)
    wrapper.setData({
      save_loading_image: true
    })
    result = wrapper.vm.get_save_loading();
    expect(result).toBe(true)

    // Video Case
    wrapper.setData({
      save_loading_frames_list: [1,2,3],
      video_mode: true
    });
    result = wrapper.vm.get_save_loading();
    expect(result).toBe(true)

  });
});
