import Vuex from "vuex";
import Vuetify from "vuetify";
import {shallowMount, createLocalVue} from "@vue/test-utils";
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
        $get_sequence_color: () => {
        },
        task: 1,
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
            }
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
      save_loading_frames_list: [1, 2, 3]
    })
    let result2 = wrapper.vm.any_frame_saving;

    expect(result2).toBe(true)
  });

  it("Tests if has_pending_frames returns correct value", () => {
    const wrapper = shallowMount(annotation_core, props, localVue);
    let result = wrapper.vm.has_pending_frames;

    expect(result).toBe(false)

    wrapper.setData({
      unsaved_frames: [1, 2, 3]
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
      save_loading_frames_list: [1, 2, 3],
      video_mode: true
    });
    result = wrapper.vm.get_save_loading(2);
    expect(result).toBe(true)

  });

  it("Tests correctly calls set_save_loading", async () => {
    const wrapper = shallowMount(annotation_core, props, localVue);

    // Image Case
    wrapper.vm.set_save_loading(true);
    expect(wrapper.vm.save_loading_image).toBe(true)

    wrapper.vm.set_save_loading(false);
    expect(wrapper.vm.save_loading_image).toBe(false)

    // Video Case
    wrapper.setData({
      video_mode: true
    })

    wrapper.vm.set_save_loading(true, 5);
    expect(wrapper.vm.save_loading_frames_list[0]).toBe(5)

    wrapper.vm.set_save_loading(false, 5);
    expect(wrapper.vm.save_loading_frames_list).toEqual([])

  });

  it("correctly calls create_instance_from_keypoints()", async () => {
    const wrapper = shallowMount(annotation_core, props, localVue);

    // Image Case
    let new_instance = wrapper.vm.create_instance_from_keypoints(5, 8);
    expect(new_instance.type).toBe('point')
    expect(new_instance.points).toEqual([{x: 5, y: 8}])

  });

  it("correctly calls create_polygon()", async () => {
    const wrapper = shallowMount(annotation_core, props, localVue);
    wrapper.vm.$refs.autoborder_alert.show_alert = () => {};
    wrapper.vm.$store.commit = () => {};
    // Image Case
    let points = [{x: 20, y: 20}, {x: 50, y: 50}, {x: 80, y: 80}];
    let id = 'test_id'
    let new_instance = wrapper.vm.create_polygon(points, id);
    expect(new_instance.type).toBe('polygon')
    expect(new_instance.points).toEqual(points)
    expect(new_instance.change_source).toEqual(`userscript_${id}`)

  });

  it("correctly calls set_keyframe_loading()", async () => {
    const wrapper = shallowMount(annotation_core, props, localVue);
    wrapper.vm.set_keyframe_loading(true);
    expect(wrapper.vm.go_to_keyframe_loading).toEqual(true)

    wrapper.vm.set_keyframe_loading(false);
    expect(wrapper.vm.go_to_keyframe_loading).toEqual(false)

  });

  it("correctly calls on_key_frame_loaded()", async () => {
    const wrapper = shallowMount(annotation_core, props, localVue);
    wrapper.vm.$store.commit = () => {};
    wrapper.vm.load_frame_instances = () => {};
    wrapper.vm.set_keyframe_loading = () => {};
    const spy = jest.spyOn(wrapper.vm, 'load_frame_instances')
    const spy2 = jest.spyOn(wrapper.vm, 'set_keyframe_loading')
    await wrapper.vm.on_key_frame_loaded();
    expect(spy).toHaveBeenCalled();
    expect(spy2).toHaveBeenCalled();

  });

  it("correctly calls load_frame_instances()", async () => {
    const wrapper = shallowMount(annotation_core, props, localVue);
    wrapper.vm.$store.commit = () => {};
    wrapper.vm.add_image_process = () => {};
    wrapper.vm.get_instances = () => {};
    wrapper.vm.ghost_refresh_instances = () => {};
    const spy = jest.spyOn(wrapper.vm, 'add_image_process')
    const spy2 = jest.spyOn(wrapper.vm, 'get_instances')
    const spy3 = jest.spyOn(wrapper.vm, 'ghost_refresh_instances')
    await wrapper.vm.load_frame_instances('https://google.com');
    expect(spy).toHaveBeenCalled();
    expect(spy2).toHaveBeenCalled();
    expect(spy3).toHaveBeenCalled();

  });

  it("correctly calls add_image_process()", async () => {
    const wrapper = shallowMount(annotation_core, {...props, canvas_wrapper:{

      }}, localVue);
    wrapper.setData({
      canvas_wrapper: {
        style:{

        }
      }
    })
    wrapper.vm.$store.commit = () => {};
    let testValue = "test";
    wrapper.vm.addImageProcess = () => testValue;
    wrapper.vm.trigger_refresh_with_delay = () => {};
    const spy = jest.spyOn(wrapper.vm, 'addImageProcess')
    const spy2 = jest.spyOn(wrapper.vm, 'trigger_refresh_with_delay')
    await wrapper.vm.add_image_process('https://google.com');
    expect(spy).toHaveBeenCalled();
    expect(spy2).toHaveBeenCalled();
    expect(wrapper.vm.loading).toEqual(false);
    expect(wrapper.vm.canvas_wrapper.style.display).toEqual("");
    expect(wrapper.vm.html_image).toEqual(testValue);

  });

  it("correctly calls set_frame_pending_save()", async () => {
    const wrapper = shallowMount(annotation_core, props, localVue);

    wrapper.vm.set_frame_pending_save(true, 95);

    expect(wrapper.vm.instance_buffer_metadata[95].pending_save).toEqual(true);
    expect(wrapper.vm.unsaved_frames[0]).toEqual(95);

    wrapper.vm.set_frame_pending_save(false, 95);

    expect(wrapper.vm.instance_buffer_metadata[95].pending_save).toEqual(false);
    expect(wrapper.vm.unsaved_frames).toEqual([]);

  });

  it("correctly calls add_instance_to_frame_buffer()", async () => {
    const wrapper = shallowMount(annotation_core, props, localVue);
    wrapper.setData({
      video_mode: true,
      instance_buffer_dict: {}
    })
    let test_instance = {};
    let frame_num = 6;
    const spy = jest.spyOn(wrapper.vm, 'set_frame_pending_save');
    wrapper.vm.add_instance_to_frame_buffer(test_instance, frame_num);
    expect(test_instance.creation_ref_id).toBeDefined();
    expect(test_instance.client_created_time).toBeDefined();
    expect(wrapper.vm.instance_buffer_dict[6][0]).toEqual(test_instance);
    expect(spy).toHaveBeenCalled();

  });

  it("correctly calls add_instance_to_file()", async () => {
    const wrapper = shallowMount(annotation_core, props, localVue);
    wrapper.setData({
      video_mode: true,
      instance_buffer_dict: {}
    })
    let test_instance = {};
    let frame_num = 6;
    const spy = jest.spyOn(wrapper.vm, 'add_instance_to_frame_buffer');
    const spy2 = jest.spyOn(wrapper.vm, 'push_instance_to_image_file');
    wrapper.vm.add_instance_to_file(test_instance, frame_num);
    expect(spy).toHaveBeenCalled();

    wrapper.setData({
      video_mode: false,
      instance_buffer_dict: {}
    })
    wrapper.vm.add_instance_to_file(test_instance, frame_num);
    expect(spy2).toHaveBeenCalled();

  });
  it("correctly calls push_instance_to_image_file()", async () => {
    const wrapper = shallowMount(annotation_core, props, localVue);
    wrapper.setData({
      video_mode: true,
      instance_buffer_dict: {}
    })
    let test_instance = {};
    let frame_num = 6;
    wrapper.vm.push_instance_to_image_file(test_instance);
    expect(test_instance.creation_ref_id).toBeDefined();
    expect(test_instance.client_created_time).toBeDefined();
    expect(wrapper.vm.instance_list).toEqual([test_instance]);
    expect(wrapper.vm.has_changed).toEqual(true);
    expect(wrapper.vm.is_actively_drawing).toEqual(false);

    wrapper.setData({
      video_mode: false,
      instance_buffer_dict: {}
    })
    wrapper.vm.add_instance_to_file(test_instance, frame_num);

  });

});
