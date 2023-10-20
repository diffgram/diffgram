import Vuex from "vuex";
import Vuetify from "vuetify";
import {shallowMount, createLocalVue} from "@vue/test-utils";
import annotation_core from "@/components/annotation/image_and_video_annotation/annotation_core.vue";
import * as InstanceUtils from "@/utils/instance_utils";
import axios from "../../../src/services/customInstance";


const vuetify = new Vuetify();
const localVue = createLocalVue();
import '@/vue-canvas.js'

localVue.use(Vuex);

jest.mock('../../../src/services/customInstance')
describe("Test annotation_core", () => {
  let props;

  beforeEach(() => {

    const store = new Vuex.Store({
      mutations: {
        'set_user_is_typing_or_menu_open': jest.fn(),
        'set_instance_select_for_issue': jest.fn(),
        'set_instance_select_for_merge': jest.fn(),
        'set_view_issue_mode': jest.fn(),
      },
      getters: {
        get_clipboard: state => {
          return {instance_list: [{x: 1}, {x: 2}]}
        }
      },
      state: {
        project: {
          current_directory: {
            directory_id: 1
          }
        },
        builder_or_trainer: {
          mode: 'builder'
        },
        clipboard: {
          clipboard_data: {
            instance_list: [],
          },
        },
        user: {
          settings: {}
        },
        annotation_state: {}

      },

    })
    props = {
      localVue,
      store,
      stubs: {
        v_bg: {
          props: {ord: 1},
          template: '<span />',
          methods: {draw: jest.fn()}
        },
        target_reticle: {
          props: {ord: 1},
          template: '<span />',
          methods: {draw: jest.fn()}
        },
        canvas_instance_list: {
          props: {ord: 1},
          template: '<span />',
          methods: {draw: jest.fn()}
        },
        ghost_instance_list_canvas: {props: {ord: 1}, template: '<span />', methods: {draw: jest.fn()}},
        canvas_current_instance: {props: {ord: 1}, template: '<span />', methods: {draw: jest.fn()}},
        current_instance_template: {props: {ord: 1}, template: '<span />', methods: {draw: jest.fn()}},

      },
      propsData: {
        hotkey_listener: {
          addScope: jest.fn(),
          addFilter: jest.fn(),
          onKeyup: jest.fn(),
          onKeydown: jest.fn(),
          onSpecialKeydown: jest.fn(),
          onSpecialKeyup: jest.fn(),
          setScopes: jest.fn()
        },
        label_schema: {
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
        canvas_wrapper: {
          style: {}
        },
        $get_sequence_color: () => {
        },
        task: 1,
        label_schema: {
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
    document.getElementById = () => {
      return {
        __vue__: {
          draw: () => {
          },
          height: 1
        },
        getContext: () => {
          return new CanvasRenderingContext2D()
        },
        draw: () => {
        },
        addEventListener: () => {
        },
        style: {}
      }
    }
  });

  it("Tests if annotation_core mounts successfully", () => {

    const wrapper = shallowMount(annotation_core, props);

    expect(wrapper.html().includes('id="annotation_core"')).toBeTruthy();
  });

  it("Tests if any_frame_saving returns correct value", () => {
    const wrapper = shallowMount(annotation_core, props);
    let result = wrapper.vm.any_frame_saving;

    expect(result).toBe(false)

    wrapper.setData({
      save_loading_frames_list: [1, 2, 3]
    })
    let result2 = wrapper.vm.any_frame_saving;

    expect(result2).toBe(true)
  });

  it("Tests if has_pending_frames returns correct value", async () => {

    const wrapper = shallowMount(annotation_core, props);

    let result = wrapper.vm.has_pending_frames;

    expect(result).toBe(false)

    await wrapper.setProps({
      has_pending_frames: true,
    })


    let result2 = wrapper.vm.has_pending_frames;

    expect(result2).toBe(true)
  });

  // THIS WAS MOVED OUT OF annoattion_core
  // it("Tests correctly calls get_save_loading", () => {
  //   const wrapper = shallowMount(annotation_core, props, localVue);

  //   // Image Case
  //   let result = wrapper.vm.get_save_loading();
  //   expect(result).toBe(false)
  //   wrapper.setData({
  //     save_loading_image: true
  //   })
  //   result = wrapper.vm.get_save_loading();
  //   expect(result).toBe(true)

  //   // Video Case
  //   wrapper.setData({
  //     save_loading_frames_list: [1, 2, 3],
  //     video_mode: true
  //   });
  //   result = wrapper.vm.get_save_loading(2);
  //   expect(result).toBe(true)

  // });

  // it("Tests correctly calls set_save_loading", async () => {
  //   const wrapper = shallowMount(annotation_core, props, localVue);

  //   // Image Case
  //   wrapper.vm.set_save_loading(true);
  //   expect(wrapper.vm.save_loading_image).toBe(true)

  //   wrapper.vm.set_save_loading(false);
  //   expect(wrapper.vm.save_loading_image).toBe(false)

  //   // Video Case
  //   wrapper.setData({
  //     video_mode: true
  //   })

  //   wrapper.vm.set_save_loading(true, 5);
  //   expect(wrapper.vm.save_loading_frames_list[0]).toBe(5)

  //   wrapper.vm.set_save_loading(false, 5);
  //   expect(wrapper.vm.save_loading_frames_list).toEqual([])

  // });

  it("correctly calls create_instance_from_keypoints()", async () => {
    const wrapper = shallowMount(annotation_core, props);

    // Image Case
    let new_instance = wrapper.vm.create_instance_from_keypoints(5, 8);
    expect(new_instance.type).toBe('point')
    expect(new_instance.points).toEqual([{x: 5, y: 8}])

  });

  it("correctly calls create_polygon()", async () => {
    const wrapper = shallowMount(annotation_core, props);
    wrapper.vm.$refs.autoborder_alert.show_alert = () => {
    };
    wrapper.vm.$store.commit = () => {
    };
    // Image Case
    let points = [{x: 20, y: 20}, {x: 50, y: 50}, {x: 80, y: 80}];
    let id = 'test_id'
    let new_instance = wrapper.vm.create_polygon(points, id);
    expect(new_instance.type).toBe('polygon')
    expect(new_instance.points).toEqual(points)
    expect(new_instance.change_source).toEqual(`userscript_${id}`)

  });

  it("correctly calls set_keyframe_loading()", async () => {
    const wrapper = shallowMount(annotation_core, props);
    wrapper.vm.set_keyframe_loading(true);
    expect(wrapper.vm.image_annotation_ctx.go_to_keyframe_loading).toEqual(true)

    wrapper.vm.set_keyframe_loading(false);
    expect(wrapper.vm.image_annotation_ctx.go_to_keyframe_loading).toEqual(false)

  });

  it("correctly calls on_key_frame_loaded()", async () => {
    const wrapper = shallowMount(annotation_core, props);
    wrapper.vm.$store.commit = () => {
    };
    wrapper.vm.load_frame_instances = () => {
    };
    wrapper.vm.set_keyframe_loading = () => {
    };
    wrapper.vm.add_image_process = () => {
    };
    const spy = jest.spyOn(wrapper.vm, 'load_frame_instances')
    const spy2 = jest.spyOn(wrapper.vm, 'set_keyframe_loading')
    const spy3 = jest.spyOn(wrapper.vm, 'add_image_process')
    await wrapper.vm.on_key_frame_loaded('https://google.com');
    expect(spy).toHaveBeenCalled();
    expect(spy2).toHaveBeenCalled();
    expect(spy3).toHaveBeenCalled();

  });

  it("correctly calls load_frame_instances()", async () => {
    const wrapper = shallowMount(annotation_core, props);
    wrapper.vm.$store.commit = () => {
    };
    wrapper.vm.get_instances = () => {
    };
    wrapper.vm.ghost_refresh_instances = () => {
    };
    const spy2 = jest.spyOn(wrapper.vm, 'get_instances')
    await wrapper.vm.load_frame_instances('https://google.com');
    expect(spy2).toHaveBeenCalled();
    expect(wrapper.emitted().ghost_refresh_instances).toBeTruthy()
  });

  it("correctly calls add_image_process()", async () => {
    const wrapper = shallowMount(annotation_core, {
      ...props, canvas_wrapper: {style: {}}
    });
    wrapper.setData({
      canvas_wrapper: {
        style: {}
      }
    })
    wrapper.vm.$store.commit = () => {
    };
    let testValue = "test";
    wrapper.vm.addImageProcess = () => testValue;
    wrapper.vm.trigger_refresh_with_delay = () => {
    };
    const spy = jest.spyOn(wrapper.vm, 'addImageProcess')
    const spy2 = jest.spyOn(wrapper.vm, 'trigger_refresh_with_delay')
    await wrapper.vm.add_image_process('https://google.com');
    expect(spy).toHaveBeenCalled();
    expect(spy2).toHaveBeenCalled();
    expect(wrapper.vm.loading).toEqual(false);
    expect(wrapper.vm.canvas_wrapper.style.display).toEqual("");
    expect(wrapper.vm.html_image).toEqual(testValue);

  });

  // THIS WAS MOVED OUT OF annotation_core
  // it("correctly calls set_frame_pending_save()", async () => {
  //   const wrapper = shallowMount(annotation_core, props, localVue);

  //   wrapper.vm.set_frame_pending_save(true, 95);

  //   expect(wrapper.vm.instance_buffer_metadata[95].pending_save).toEqual(true);
  //   expect(wrapper.vm.unsaved_frames[0]).toEqual(95);

  //   wrapper.vm.set_frame_pending_save(false, 95);

  //   expect(wrapper.vm.instance_buffer_metadata[95].pending_save).toEqual(false);
  //   expect(wrapper.vm.unsaved_frames).toEqual([]);

  // });

  it("correctly calls add_instance_to_frame_buffer()", async () => {
    const wrapper = shallowMount(annotation_core, props);
    wrapper.setData({
      image_annotation_ctx: {
        label_settings: {},
        video_mode: true,
      },
      instance_buffer_dict: {}
    })
    let test_instance = {};
    let frame_num = 6;
    await wrapper.vm.add_instance_to_frame_buffer(test_instance, frame_num);
    expect(test_instance.creation_ref_id).toBeDefined();
    expect(test_instance.client_created_time).toBeDefined();
    expect(wrapper.vm.instance_buffer_dict[6][0]).toEqual(test_instance);

    expect(wrapper.emitted().set_frame_pending_save).toBeTruthy()
  });

  it("correctly calls add_instance_to_file()", async () => {
    const wrapper = shallowMount(annotation_core, props);
    wrapper.setData({
      image_annotation_ctx: {
        video_mode: true,
        label_settings: {},
      },
      instance_buffer_dict: {}
    })
    let test_instance = {};
    let frame_num = 6;
    const spy = jest.spyOn(wrapper.vm, 'add_instance_to_frame_buffer');
    const spy2 = jest.spyOn(wrapper.vm, 'push_instance_to_image_file');
    wrapper.vm.add_instance_to_file(test_instance, frame_num);
    expect(spy).toHaveBeenCalled();

    wrapper.setData({
      image_annotation_ctx: {
        video_mode: false,
        label_settings: {},
      },
      instance_buffer_dict: {}
    })
    wrapper.vm.add_instance_to_file(test_instance, frame_num);
    expect(spy2).toHaveBeenCalled();

  });
  // it("correctly calls push_instance_to_image_file()", async () => {
  //   const wrapper = shallowMount(annotation_core, props, localVue);
  //   wrapper.setData({
  //     video_mode: true,
  //     instance_buffer_dict: {}
  //   })
  //   let test_instance = {};
  //   let frame_num = 6;
  //   wrapper.vm.push_instance_to_image_file(test_instance);
  //   expect(test_instance.creation_ref_id).toBeDefined();
  //   expect(test_instance.client_created_time).toBeDefined();
  //   expect(wrapper.vm.instance_list).toEqual([test_instance]);
  //   expect(wrapper.vm.has_changed).toEqual(true);
  //   expect(wrapper.vm.is_actively_drawing).toEqual(false);

  //   wrapper.setData({
  //     video_mode: false,
  //     instance_buffer_dict: {}
  //   })
  //   wrapper.vm.add_instance_to_file(test_instance, frame_num);

  // });

  // it("correctly calls finish_polygon_drawing()", async () => {
  //   const wrapper = shallowMount(annotation_core, props, localVue);
  //   wrapper.vm.command_manager.executeCommand = () => {
  //   }
  //   wrapper.setData({
  //     video_mode: true,
  //     is_actively_drawing: true,
  //     instance_type: 'polygon',
  //     instance_buffer_dict: {},
  //     current_instance: {
  //       points: [
  //         {},
  //         {},
  //         {}
  //       ]
  //     }
  //   })
  //   const spy = jest.spyOn(wrapper.vm.command_manager, 'executeCommand');

  //   const mock_event = {
  //     keyCode: 13
  //   }

  //   wrapper.vm.finish_polygon_drawing(mock_event);
  //   expect(wrapper.vm.is_actively_drawing).toEqual(false);
  //   expect(wrapper.vm.current_polygon_point_list).toEqual([]);
  //   expect(spy).toHaveBeenCalled();

  // });


  it("correctly calls paste_instance()", async () => {
    const wrapper = shallowMount(annotation_core, props);
    wrapper.vm.$store.commit = () => {
    }

    wrapper.setData({full_file_loading: false})

    wrapper.vm.add_pasted_instance_to_instance_list = () => {
    }

    let test_instance = {};
    let frame_num = 6;

    const spy = jest.spyOn(wrapper.vm, 'copy_instance');
    const spy2 = jest.spyOn(InstanceUtils, 'duplicate_instance');
    const spy3 = jest.spyOn(wrapper.vm, 'add_pasted_instance_to_instance_list');
    const spy4 = jest.spyOn(wrapper.vm, 'set_clipboard');


    await wrapper.vm.paste_instance(undefined, 1, undefined);

    expect(spy).toHaveBeenCalled();
    expect(spy2).toHaveBeenCalledTimes(2);
    expect(spy3).toHaveBeenCalledTimes(2);
    expect(spy4).toHaveBeenCalled();

  });
  it("correctly calls calculate_min_max_points()", async () => {
    const wrapper = shallowMount(annotation_core, props);
    // Curve type
    let instance = {
      type: 'point'
    };
    // Point
    wrapper.vm.calculate_min_max_points(instance)
    expect(instance.x_min).toBeUndefined();
    expect(instance.y_min).toBeUndefined();
    expect(instance.x_max).toBeUndefined();
    expect(instance.y_max).toBeUndefined();
    instance.points = [{x: 5, y: 5}, {x: 10, y: 10}]
    wrapper.vm.calculate_min_max_points(instance)
    expect(instance.x_min).toBe(5);
    expect(instance.y_min).toBe(5);
    expect(instance.x_max).toBe(10);
    expect(instance.y_max).toBe(10);
    // Polygon
    instance.type = 'polygon'
    wrapper.vm.calculate_min_max_points(instance)
    expect(instance.x_min).toBe(5);
    expect(instance.y_min).toBe(5);
    expect(instance.x_max).toBe(10);
    expect(instance.y_max).toBe(10);
    // Cuboid
    instance = {
      type: 'cuboid'
    };
    wrapper.vm.calculate_min_max_points(instance)
    expect(instance.x_min).toBeUndefined();
    expect(instance.y_min).toBeUndefined();
    expect(instance.x_max).toBeUndefined();
    expect(instance.y_max).toBeUndefined();
    instance.front_face = {
      top_right: {x: 1, y: 1},
      bot_right: {x: 1, y: 1},
      top_left: {x: 1, y: 1},
      bot_left: {x: 1, y: 1},
    }
    instance.rear_face = {
      top_right: {x: 1, y: 1},
      bot_right: {x: 15, y: 1},
      top_left: {x: 1, y: 17},
      bot_left: {x: 1, y: 1},
    }
    wrapper.vm.calculate_min_max_points(instance)
    expect(instance.x_min).toBe(1);
    expect(instance.y_min).toBe(1);
    expect(instance.x_max).toBe(15);
    expect(instance.y_max).toBe(17);
    // ellipse
    instance = {
      type: 'ellipse'
    };
    wrapper.vm.calculate_min_max_points(instance)
    expect(instance.x_min).toBeUndefined();
    expect(instance.y_min).toBeUndefined();
    expect(instance.x_max).toBeUndefined();
    expect(instance.y_max).toBeUndefined();
    instance.center_x = 60;
    instance.center_y = 60;
    instance.width = 25;
    instance.height = 25;
    wrapper.vm.calculate_min_max_points(instance)
    expect(instance.x_min).toBe(35);
    expect(instance.y_min).toBe(35);
    expect(instance.x_max).toBe(85);
    expect(instance.y_max).toBe(85);
    // curve
    instance = {
      type: 'curve'
    };
    wrapper.vm.calculate_min_max_points(instance)
    expect(instance.x_min).toBeUndefined();
    expect(instance.y_min).toBeUndefined();
    expect(instance.x_max).toBeUndefined();
    expect(instance.y_max).toBeUndefined();
    instance.p1 = {x: 5, y: 8};
    instance.p2 = {x: 55, y: 78}
    wrapper.vm.calculate_min_max_points(instance)
    expect(instance.x_min).toBe(5);
    expect(instance.y_min).toBe(8);
    expect(instance.x_max).toBe(55);
    expect(instance.y_max).toBe(78);
    instance = {
      type: 'any_other_type'
    };
    instance.x_min = 7
    instance.y_min = 8
    instance.x_max = 9
    instance.y_max = 9
    wrapper.vm.calculate_min_max_points(instance)
    expect(instance.x_min).toBe(instance.x_min);
    expect(instance.y_min).toBe(instance.y_min);
    expect(instance.x_max).toBe(instance.x_max);
    expect(instance.y_max).toBe(instance.y_max);
  });

  it("correctly pans when z key is pressed", async () => {
    const wrapper = shallowMount(annotation_core, props);
    wrapper.vm.$store.commit = () => {
    }

    wrapper.vm.move_position_based_on_mouse = () => {
    };
    wrapper.vm.move_something = () => {
    };
    wrapper.vm.mouse_transform = () => ({x: 25, y: 25});
    wrapper.vm.helper_difference_absolute = () => {
    };
    wrapper.vm.update_mouse_style = () => {
    };
    wrapper.vm.detect_other_polygon_points = () => {
    };
    wrapper.vm.instance_insert_point = () => {
    };
    wrapper.vm.generate_event_interactions = () => {
    };

    const spy = jest.spyOn(wrapper.vm, 'move_position_based_on_mouse');
    wrapper.setData({
      z_key: true,
      instance_type: 'polygon',
      mouse_position: {x: 25, y: 25},
      current_polygon_point_list: [{x: 1, y: 1}],
      canvas_element: {
        style: {
          cursor: 'auto'
        }
      },
      canvas_mouse_tools: {
        mouse_transform: () => {
        }
      }
    })
    let event = {};
    await wrapper.vm.mouse_move(event);

    expect(spy).toHaveBeenCalled();
  });
});
