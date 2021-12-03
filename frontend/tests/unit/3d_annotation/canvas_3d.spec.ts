import Vuex from "vuex";
import {shallowMount, createLocalVue, Wrapper} from "@vue/test-utils";
import canvas_3d from "../../../src/components/3d_annotation/canvas_3d.vue";
import 'jest-canvas-mock';
import * as THREE from "three";
import {WEBGL} from "../../../src/components/3d_annotation/WebGL";
import mock = jest.mock;

jest.mock("three/src/renderers/WebGLRenderer"); // this happens automatically with automocking
const localVue = createLocalVue();
localVue.use(Vuex);


window.alert = jest.fn();

class MockClassWebGLRenderer {
  setPixelRatio = jest.fn();
  setSize = jest.fn();
}

const create_test_mesh = function () {
  let geometry = new THREE.BoxGeometry(2, 2, 2);
  let material = new THREE.MeshBasicMaterial({
    color: new THREE.Color('red'),
    opacity: 1,
    transparent: true,
  });
  let mesh = new THREE.Mesh(geometry, material);
  return mesh
}

describe("Test canvas_3d.vue", () => {
  let options;
  let wrapper: Wrapper<Vue>;
  beforeEach(() => {
    let WebGLRendererModule = require("three/src/renderers/WebGLRenderer");

    // @ts-ignore
    THREE.WebGLRenderer = MockClassWebGLRenderer
    options = {

      propsData: {
        pan_speed: 48,
        zoom_speed: 85,
        container_id: 'test_canvas_3d',
        point_cloud_mesh: create_test_mesh(),
      },
      mocks: {
        $get_sequence_color: () => {
        },
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
            get_view_issue_mode: () => {
            }
          }
        }
      }
    };
    Object.defineProperty(HTMLElement.prototype, 'clientWidth', {configurable: true, value: 500})
    Object.defineProperty(HTMLElement.prototype, 'clientHeight', {configurable: true, value: 500})
  });

  it("Tests if canvas_3d mounts successfully", () => {
    wrapper = shallowMount(canvas_3d, options);
    wrapper.setData({
      container: {
        clientWidth: 0,
        clientHeight: 0
      }
    })
    expect(wrapper.html().includes(`id="${options.propsData.container_id}"`)).toBeTruthy();
  });

  it("Adds orbit controls when calling on_focus_canvas()", () => {
    wrapper = shallowMount(canvas_3d, options);
    let vm = wrapper.vm as any;
    wrapper.setData({
      scene_controller: {
        add_orbit_controls_events: () => {
        }
      },
      container: {
        clientWidth: 0,
        clientHeight: 0
      }
    })
    const spy = jest.spyOn(vm.scene_controller, 'add_orbit_controls_events')
    vm.on_focus_canvas();
    expect(spy).toHaveBeenCalled()
  });

  it("Removes orbit controls when calling on_focus_out_canvas()", () => {
    wrapper = shallowMount(canvas_3d, options);
    let vm = wrapper.vm as any;
    wrapper.setData({
      scene_controller: {
        remove_orbit_controls_events: () => {
        }
      },
      container: {
        clientWidth: 0,
        clientHeight: 0
      }
    })
    const spy = jest.spyOn(vm.scene_controller, 'remove_orbit_controls_events')
    vm.on_focus_out_canvas();
    expect(spy).toHaveBeenCalled()
  });

  it("Executes correct actions when calling on_key_down()", () => {
    wrapper = shallowMount(canvas_3d, options);
    let vm = wrapper.vm as any;
    wrapper.setData({
      point_cloud_mesh: {
        geometry: {
          dispose: () => {
          }
        },
        material: {
          dispose: () => {
          }
        }
      },
      scene_controller: {
        center_camera_to_mesh: () => {
        }
      },
      container: {
        clientWidth: 0,
        clientHeight: 0
      }
    })
    const spy = jest.spyOn(vm, 'center_camera')
    vm.on_key_down({keyCode: 67});
    expect(spy).toHaveBeenCalled()
  });

  it("Setups scene when calling load_canvas()", () => {
    WEBGL.isWebGLAvailable = () => {
      return true
    };
    wrapper = shallowMount(canvas_3d, options);

    let vm = wrapper.vm as any;
    wrapper.setData({
      scene: {
        remove: jest.fn()
      },
      scene_controller: {
        center_camera_to_mesh: () => {
        }
      },
      container: {
        clientWidth: 0,
        clientHeight: 0
      }
    })
    const spy = jest.spyOn(vm, 'setup_scene')
    vm.load_canvas();
    expect(spy).toHaveBeenCalledTimes(1);

    WEBGL.isWebGLAvailable = () => {
      return false
    };
    const spy2 = jest.spyOn(vm, 'setup_scene')
    vm.load_canvas();
    expect(spy2).toHaveBeenCalledTimes(1); // Should still be 1 instead of 2 because mock now returns false.
  });

  it("Correctly destroys the scene when calling destroy_canvas()", () => {
    wrapper = shallowMount(canvas_3d, options);

    let vm = wrapper.vm as any;
    wrapper.setData({
      scene_controller: {
        scene: {
          remove: () => {
          }
        },
        detach_mouse_events: () => {
        },
        clear_all: () => {
        },
        remove_orbit_controls_events: () => {
        }
      },
      container: {
        clientWidth: 0,
        clientHeight: 0
      }

    })
    const spy_detach_mouse_events = jest.spyOn(vm.scene_controller, 'detach_mouse_events')
    const spy_remove_orbit_controls_events = jest.spyOn(vm.scene_controller, 'remove_orbit_controls_events')
    const spy_remove_scene = jest.spyOn(vm.scene_controller.scene, 'remove')
    const spy_clear_all = jest.spyOn(vm.scene_controller, 'clear_all')
    const spy_dispose_geometry = jest.spyOn(vm.point_cloud_mesh.geometry, 'dispose')
    const spy_dispose_material = jest.spyOn(vm.point_cloud_mesh.material, 'dispose')
    vm.destroy_canvas();
    expect(spy_detach_mouse_events).toHaveBeenCalledTimes(1);
    expect(spy_remove_orbit_controls_events).toHaveBeenCalledTimes(1);
    expect(spy_remove_scene).toHaveBeenCalledTimes(1);
    expect(spy_clear_all).toHaveBeenCalledTimes(1);
    expect(spy_dispose_geometry).toHaveBeenCalledTimes(1);
    expect(spy_dispose_material).toHaveBeenCalledTimes(1);

  });

  it("Correctly calls update_pan_speed()", () => {
    wrapper = shallowMount(canvas_3d, options);

    let vm = wrapper.vm as any;
    wrapper.setData({
      scene_controller: {
        controls_orbit: {
          update: jest.fn()
        },
        scene: {
          remove: () => {
          }
        },
        detach_mouse_events: () => {
        },
        clear_all: () => {
        },
        remove_orbit_controls_events: () => {
        }
      },
      container: {
        clientWidth: 0,
        clientHeight: 0
      }

    })
    const spy_update = jest.spyOn(vm.scene_controller.controls_orbit, 'update')

    vm.update_pan_speed();
    expect(spy_update).toHaveBeenCalledTimes(1);
    expect(vm.scene_controller.controls_orbit.panSpeed).toEqual(options.propsData.pan_speed)

  });

  it("Correctly calls update_zoom_speed()", () => {
    wrapper = shallowMount(canvas_3d, options);

    let vm = wrapper.vm as any;
    wrapper.setData({
      scene_controller: {
        controls_orbit: {
          update: jest.fn()
        },
        scene: {
          remove: () => {
          }
        },
        detach_mouse_events: () => {
        },
        clear_all: () => {
        },
        remove_orbit_controls_events: () => {
        }
      },
      container: {
        clientWidth: 0,
        clientHeight: 0
      }

    })
    const spy_update = jest.spyOn(vm.scene_controller.controls_orbit, 'update')

    vm.update_zoom_speed();
    expect(spy_update).toHaveBeenCalledTimes(1);
    expect(vm.scene_controller.controls_orbit.zoomSpeed).toEqual(options.propsData.zoom_speed)

  });

  it("Correctly calls setup_ortographic_scene_controller()", () => {
    wrapper = shallowMount(canvas_3d, options);
    wrapper.setData({
      renderer: {
        setPixelRatio: jest.fn()
      },
      container: {
        clientWidth: 0,
        clientHeight: 0,
        addEventListener: jest.fn()
      }
    })
    let scene_mock = {
      add: jest.fn(),
    }
    let vm = wrapper.vm as any;
    vm.setup_ortographic_scene_controller(scene_mock);
    expect(vm.camera).toBeDefined()
    expect(vm.scene_controller).toBeDefined()

  });

  it("Correctly calls setup_perspective_scene_controller()", () => {
    wrapper = shallowMount(canvas_3d, options);
    wrapper.setData({
      renderer: {
        setPixelRatio: jest.fn()
      },
      container: {
        clientWidth: 0,
        clientHeight: 0
      }

    })
    let scene_mock = {
      add: jest.fn(),
    }
    let vm = wrapper.vm as any;
    vm.setup_perspective_scene_controller(scene_mock);
    expect(vm.camera).toBeDefined()
    expect(vm.scene_controller).toBeDefined()

  });

  it("Correctly calls create_renderer()", () => {
    wrapper = shallowMount(canvas_3d, options);
    let WebGLRendererModule = require("three/src/renderers/WebGLRenderer");

    // @ts-ignore
    THREE.WebGLRenderer = MockClassWebGLRenderer
    wrapper.setData({
      renderer: {
        setPixelRatio: jest.fn()
      },
      container: {
        clientWidth: 0,
        clientHeight: 0
      }

    })
    let vm = wrapper.vm as any;

    vm.create_renderer();
    expect(vm.renderer).toBeDefined()

  });

  it("Correctly calls setup_scene()", () => {
    options.propsData.camera_type = 'perspective';
    wrapper = shallowMount(canvas_3d, options);
    wrapper.setData({
      container: {
        clientWidth: 0,
        clientHeight: 0
      },
      renderer: {
        domElement: document.createElement('canvas')
      }

    })
    let spy = jest.spyOn(document, 'getElementById');
    let mockdiv = document.createElement('div')
    mockdiv.style.width = 100 + "px";
    mockdiv.style.height = 100 + "px";
    document.body.appendChild(mockdiv);
    spy.mockReturnValue(mockdiv);
    let vm = wrapper.vm as any;
    vm.create_renderer = jest.fn();
    vm.setup_perspective_scene_controller = jest.fn();
    const spy_create_renderer = jest.spyOn(vm, 'create_renderer')
    const spy_add_event_listener = jest.spyOn(window, 'addEventListener')
    const spy_setup_perspective_scene_controller = jest.spyOn(vm, 'setup_perspective_scene_controller')
    const spy_configure_controls = jest.spyOn(vm, 'configure_controls')

    vm.setup_scene({});
    expect(spy_create_renderer).toHaveBeenCalledTimes(0);
    expect(spy_add_event_listener).toHaveBeenCalledTimes(1);
    expect(spy_add_event_listener).toHaveBeenCalledTimes(1);
    expect(spy_setup_perspective_scene_controller).toHaveBeenCalledTimes(1);
    expect(spy_configure_controls).toHaveBeenCalledTimes(1);

  });

  it("Correctly calls set_current_label_file()", () => {
    wrapper = shallowMount(canvas_3d, options);

    let vm = wrapper.vm as any;
    wrapper.setData({
      scene_controller: {
        controls_orbit: {
          update: jest.fn()
        },
        scene: {
          remove: () => {
          }
        },
        set_current_label_file: () => {
        },
        clear_all: () => {
        },
        remove_orbit_controls_events: () => {
        }
      },
      container: {
        clientWidth: 0,
        clientHeight: 0
      }

    })
    const spy_set_current_label_file = jest.spyOn(vm.scene_controller, 'set_current_label_file')

    vm.set_current_label_file();
    expect(spy_set_current_label_file).toHaveBeenCalledTimes(1);

  });

  it("Correctly calls set_draw_mode()", () => {
    wrapper = shallowMount(canvas_3d, options);

    let vm = wrapper.vm as any;
    wrapper.setData({
      scene_controller: {
        controls_orbit: {
          update: jest.fn()
        },
        scene: {
          remove: () => {
          }
        },
        set_current_label_file: () => {
        },
        clear_all: () => {
        },
        set_draw_mode: () => {
        }
      },
      container: {
        clientWidth: 0,
        clientHeight: 0
      }

    })
    const spy_set_draw_mode = jest.spyOn(vm.scene_controller, 'set_draw_mode')

    vm.set_draw_mode();
    expect(spy_set_draw_mode).toHaveBeenCalledTimes(1);

  });

  it("Correctly calls add_instance_list_to_scene()", () => {
    options.propsData.instance_list = [
      {
        draw_on_scene: jest.fn()
      },
      {
        draw_on_scene: jest.fn()
      },
      {
        draw_on_scene: jest.fn()
      }
    ]
    wrapper = shallowMount(canvas_3d, options);

    let vm = wrapper.vm as any;
    const spy_draw_1 = jest.spyOn(vm.instance_list[0], 'draw_on_scene')
    const spy_draw_2 = jest.spyOn(vm.instance_list[1], 'draw_on_scene')
    const spy_draw_3 = jest.spyOn(vm.instance_list[2], 'draw_on_scene')

    vm.add_instance_list_to_scene();
    expect(spy_draw_1).toHaveBeenCalledTimes(1);
    expect(spy_draw_2).toHaveBeenCalledTimes(1);
    expect(spy_draw_3).toHaveBeenCalledTimes(1);

  });

  it("Correctly calls update_camera_aspect_ratio()", () => {
    wrapper = shallowMount(canvas_3d, options);
    wrapper.setData({
      container: {
        clientWidth: 1,
        clientHeight: 1
      },
      renderer:{
        setSize: jest.fn(),
      },
      camera: {
        updateProjectionMatrix: jest.fn(),
      }
    })
    let vm = wrapper.vm as any;
    const spy_1 = jest.spyOn(vm.camera, 'updateProjectionMatrix')
    const spy_2 = jest.spyOn(vm.renderer, 'setSize')

    vm.update_camera_aspect_ratio();
    expect(spy_1).toHaveBeenCalledTimes(1);
    expect(spy_2).toHaveBeenCalledTimes(1);

  });

  it("Correctly calls on_window_resize()", () => {
    wrapper = shallowMount(canvas_3d, options);
    wrapper.setData({
      container: {
        clientWidth: 1,
        clientHeight: 1
      },
      renderer:{
        setSize: jest.fn(),
      },
      camera: {
        updateProjectionMatrix: jest.fn(),
      }
    })
    let vm = wrapper.vm as any;
    const spy_1 = jest.spyOn(vm, 'update_camera_aspect_ratio')

    vm.on_window_resize();
    expect(spy_1).toHaveBeenCalledTimes(1);

  });

  it("Correctly calls center_camera()", () => {
    wrapper = shallowMount(canvas_3d, options);
    wrapper.setData({
      scene_controller: {
        center_camera_to_mesh: () => {
        }
      },
      container: {
        clientWidth: 0,
        clientHeight: 0
      }
    })
    let vm = wrapper.vm as any;
    const spy_1 = jest.spyOn(vm.scene_controller, 'center_camera_to_mesh')

    vm.center_camera();
    expect(spy_1).toHaveBeenCalledTimes(1);

  });

  it("Correctly calls configure_controls()", () => {
    options.propsData.allow_navigation = true
    wrapper = shallowMount(canvas_3d, options);
    wrapper.setData({
      scene_controller: {
        controls_orbit: {

        },
        add_orbit_controls: () => {},
        add_transform_controls: () => {},
      },
      container: {
        clientWidth: 0,
        clientHeight: 0
      }
    })
    let vm = wrapper.vm as any;
    const spy_1 = jest.spyOn(vm.scene_controller, 'add_transform_controls')
    const spy_2 = jest.spyOn(vm.scene_controller, 'add_orbit_controls')

    vm.configure_controls();
    expect(spy_1).toHaveBeenCalledTimes(1);
    expect(spy_2).toHaveBeenCalledTimes(1);


  });


});
