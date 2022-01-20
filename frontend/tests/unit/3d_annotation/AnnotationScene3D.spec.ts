import Vuex from "vuex";
import Vue from "vue";
import * as THREE from "three";
import {shallowMount, createLocalVue, Wrapper} from "@vue/test-utils";
import ObjectTransformControls from "../../../src/components/3d_annotation/ObjectTransformControls";
import AnnotationScene3D from "../../../src/components/3d_annotation/AnnotationScene3D";
import axios from "axios";
import {mocked} from 'ts-jest/utils'
import {load} from "mime";
import mock = jest.mock;
import {create_test_mesh} from './3d_mocks'
import {OrbitControls} from "../../../src/components/3d_annotation/OrbitControls";

axios.defaults.adapter = require('axios/lib/adapters/http')

jest.mock("three/src/renderers/WebGLRenderer"); // this happens automatically with automocking
const localVue = createLocalVue();
localVue.use(Vuex);



window.alert = jest.fn();

describe("Test ObjectTransformControls.spec.ts", () => {
  let controls, domeElement,
    scene,
    camera,
    controls_panning_speed,
    point_cloud_mesh,
    renderer,
    instance_list,
    container,
    controller,
    component_ctx,
    layer_number;
  let wrapper: Wrapper<Vue>;
  beforeEach(() => {
    component_ctx = new Vue();

    domeElement = document.createElement('canvas');
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, 0.5, 0.1, 1000);
    instance_list = []
    controls_panning_speed = 60;
    point_cloud_mesh = mocked(THREE.Mesh, true) as unknown as THREE.Mesh;
    ;
    renderer = {
      setPixelRatio: jest.fn()
    };
    container = document.createElement('setPixelRatio');
    layer_number = 1;


  });

  it("Correctly creates a SceneController3D() object", () => {
    let spy = jest.spyOn(renderer, 'setPixelRatio')
    let spy2 = jest.spyOn(scene, 'add')

    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );

    expect(controller.scene).toBe(scene);
    expect(controller.camera).toBe(camera);
    expect(controller.renderer).toBe(renderer);
    expect(spy).toHaveBeenCalled()
    expect(controller.container).toBe(container);
    expect(controller.component_ctx).toBe(component_ctx);
    expect(controller.point_cloud_mesh).toBe(point_cloud_mesh);
    expect(controller.controls_panning_speed).toBe(controls_panning_speed);
    expect(controller.mouse).toBeInstanceOf(THREE.Vector2);
    expect(controller.plane_normal).toBeInstanceOf(THREE.Vector3);
    expect(controller.mouse_position_3d).toBeInstanceOf(THREE.Vector3);
    expect(controller.raycaster).toBeInstanceOf(THREE.Raycaster);
    expect(controller.axes_helper).toBeInstanceOf(THREE.AxesHelper);
    expect(controller.grid_helper).toBeInstanceOf(THREE.GridHelper);
    expect(controller.plane).toBeInstanceOf(THREE.Plane);
    expect(controller.instance_list).toBeDefined();
    expect(spy2).toHaveBeenCalledTimes(2)

  });

  it("Correctly calls clear_all()", () => {
    renderer.setAnimationLoop = jest.fn()
    renderer.domElement = document.createElement('canvas')


    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    let spy = jest.spyOn(renderer, 'setAnimationLoop')
    let spy2 = jest.spyOn(scene, 'remove')
    controller.clear_all()
    expect(spy).toHaveBeenCalledTimes(3)
    expect(spy2).toHaveBeenCalledTimes(2)

  });

  it("Correctly calls reset_materials()", () => {
    renderer.setAnimationLoop = jest.fn()
    renderer.domElement = document.createElement('canvas')
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    controller.draw_mode = false;
    controller.selected_instance = {
      mesh: create_test_mesh()
    }
    let mesh1 = create_test_mesh();
    let mesh2 = create_test_mesh();
    scene.add(mesh1)
    scene.add(mesh2)
    scene.add(controller.selected_instance.mesh)
    let spy = jest.spyOn(mesh1.material.color, 'set')
    let spy2 = jest.spyOn(mesh2.material.color, 'set')
    controller.reset_materials();

    expect(mesh1.material.opacity).toBe(0.6)
    expect(mesh2.material.opacity).toBe(0.6)
    expect(spy).toHaveBeenCalled()
    expect(spy2).toHaveBeenCalled()
    expect(controller.selected_instance.mesh.material.opacity).toBe(0.9)

  });

  it("Correctly calls get_current_color()", () => {
    renderer.setAnimationLoop = jest.fn()
    renderer.domElement = document.createElement('canvas')
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    controller.label_file = {
      colour: {
        hex: 'test'
      }
    }
    let result = controller.get_current_color();

    expect(result).toBe(controller.label_file.colour.hex)

  });

  it("Correctly calls on_drag_transform_controls()", () => {
    renderer.setAnimationLoop = jest.fn()
    renderer.domElement = document.createElement('canvas')
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    controller.controls_orbit = {
      enabled: false
    }
    let result = controller.on_drag_transform_controls({value: false});

    expect(controller.controls_orbit.enabled).toBe(true)

  });

  it("Correctly calls on_mouse_click()", () => {
    renderer.setAnimationLoop = jest.fn()
    renderer.domElement = document.createElement('canvas')
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    controller.controls_orbit = {
      enabled: false
    }
    controller.draw_mode = true;
    let spy = jest.spyOn(controller, 'on_click_draw_mode')
    let spy2 = jest.spyOn(controller, 'on_click_edit_mode')
    controller.on_mouse_click({value: false});

    expect(spy).toHaveBeenCalledTimes(1)
    expect(spy2).toHaveBeenCalledTimes(0)
    jest.clearAllMocks();
    controller.draw_mode = false;
    spy = jest.spyOn(controller, 'on_click_draw_mode')
    spy2 = jest.spyOn(controller, 'on_click_edit_mode')
    controller.on_mouse_click({value: false});

    expect(spy).toHaveBeenCalledTimes(0)
    expect(spy2).toHaveBeenCalledTimes(1)

  });

  it("Correctly calls on_mouse_double_click()", () => {
    renderer.setAnimationLoop = jest.fn()
    renderer.domElement = document.createElement('canvas')
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    controller.controls_orbit = {
      enabled: false
    }
    controller.draw_mode = true;
    let event = {value: false, stopPropagation: jest.fn()}
    let spy = jest.spyOn(controller, 'on_double_click_draw_mode')
    let spy2 = jest.spyOn(controller, 'on_double_click_edit_mode')
    let spy3 = jest.spyOn(event, 'stopPropagation')
    controller.on_mouse_double_click(event);

    expect(spy).toHaveBeenCalled()
    expect(spy3).toHaveBeenCalled()
    expect(spy2).toHaveBeenCalledTimes(0)
    jest.clearAllMocks();
    controller.draw_mode = false;
    spy = jest.spyOn(controller, 'on_double_click_draw_mode')
    spy2 = jest.spyOn(controller, 'on_double_click_edit_mode')
    spy3 = jest.spyOn(event, 'stopPropagation')
    controller.on_mouse_double_click(event);

    expect(spy).toHaveBeenCalledTimes(0)
    expect(spy3).toHaveBeenCalledTimes(1)
    expect(spy2).toHaveBeenCalledTimes(1)

  });

  it("Correctly calls on_double_click_edit_mode()", () => {
    renderer.setAnimationLoop = jest.fn()
    renderer.domElement = document.createElement('canvas')
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    controller.object_transform_controls = {}
    controller.draw_mode = true;
    let event = {value: false, stopPropagation: jest.fn()}
    let spy = jest.spyOn(controller, 'deselect_instance')

    controller.on_double_click_edit_mode(event);
    expect(spy).toHaveBeenCalled()


  });

  it("Correctly calls on_double_click_draw_mode()", () => {
    renderer.setAnimationLoop = jest.fn()
    renderer.domElement = document.createElement('canvas')
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    controller.cuboid_drawer_tool = {
      create_place_holder_cuboid: jest.fn()
    }
    controller.draw_mode = true;
    controller.currently_drawing_instance = false;
    let event = {value: false, stopPropagation: jest.fn()}
    let spy = jest.spyOn(controller.cuboid_drawer_tool, 'create_place_holder_cuboid')

    controller.on_double_click_draw_mode(event);
    expect(controller.currently_drawing_instance).toBe(true)
    expect(spy).toHaveBeenCalled()


  });

  it("Correctly calls on_click_draw_mode()", () => {
    renderer.setAnimationLoop = jest.fn()
    renderer.domElement = document.createElement('canvas')
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    controller.cuboid_drawer_tool = {
      place_holder_cuboid: {},
      create_place_holder_cuboid: jest.fn(),
      remove_placeholder_cuboid: jest.fn()
    }
    controller.draw_mode = true;
    controller.add_cube_to_instance_list = jest.fn()
    controller.select_instance = jest.fn()
    controller.currently_drawing_instance = true;
    let event = {value: false, stopPropagation: jest.fn()}
    let spy = jest.spyOn(controller, 'set_draw_mode')
    let spy2 = jest.spyOn(controller, 'add_cube_to_instance_list')
    let spy3 = jest.spyOn(controller, 'select_instance')
    let spy4 = jest.spyOn(controller.component_ctx, '$emit')

    controller.on_click_draw_mode(event);
    expect(spy).toHaveBeenCalledWith(false)
    expect(spy2).toHaveBeenCalled()
    expect(spy3).toHaveBeenCalled()
    expect(spy4).toHaveBeenCalled()


  });

  it("Correctly calls update_mouse_position()", () => {
    renderer.setAnimationLoop = jest.fn()
    renderer.domElement = {
      getBoundingClientRect: () => ({
        left: 5,
        top: 5
      })
    }
    let rect = renderer.domElement.getBoundingClientRect()
    let event = {clientX: 1, clientY: 6}
    let x = event.clientX - rect.left;
    let y = event.clientY - rect.top;
    container = {
      clientWidth: 45,
      clientHeight: 3,
    }
    let mouse_x = (x / container.clientWidth) * 2 - 1;
    let mouse_y = -(y / container.clientHeight) * 2 + 1;

    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );

    controller.cuboid_drawer_tool = {
      place_holder_cuboid: {},
      create_place_holder_cuboid: jest.fn(),
      remove_placeholder_cuboid: jest.fn()
    }

    let spy = jest.spyOn(controller, 'get_3d_mouse_position')
    let spyEmit = jest.spyOn(controller.component_ctx, '$emit')
    controller.update_mouse_position(event);
    expect(controller.mouse.x).toBe(mouse_x)
    expect(controller.mouse.y).toBe(mouse_y)
    expect(spy).toHaveBeenCalled();
    expect(spyEmit).toHaveBeenCalledWith('updated_mouse_position', {
      x: mouse_x,
      y: mouse_y,
      screen_y: y,
      screen_x: x
    });

  });

  it("Correctly calls on_mouse_move()", () => {
    renderer.setAnimationLoop = jest.fn()
    renderer.domElement = {
      getBoundingClientRect: () => ({
        left: 5,
        top: 5
      })
    }
    let rect = renderer.domElement.getBoundingClientRect()
    let event = {clientX: 1, clientY: 6}
    let x = event.clientX - rect.left;
    let y = event.clientY - rect.top;
    container = {
      clientWidth: 45,
      clientHeight: 3,
    }
    let mouse_x = (x / container.clientWidth) * 2 - 1;
    let mouse_y = -(y / container.clientHeight) * 2 + 1;

    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    controller.cuboid_drawer_tool = {
      place_holder_cuboid: {},
      resize_place_holder_cuboid: jest.fn(),
      remove_placeholder_cuboid: jest.fn()
    }
    controller.draw_mode = true;
    controller.currently_drawing_instance = true;
    let spy = jest.spyOn(controller, 'update_mouse_position')
    let spy2 = jest.spyOn(controller.cuboid_drawer_tool, 'resize_place_holder_cuboid')
    controller.on_mouse_move(event);
    expect(spy).toHaveBeenCalled()
    expect(spy2).toHaveBeenCalled()

  });

  it("Correctly calls get_3d_mouse_position()", () => {
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    controller.cuboid_drawer_tool = {
      place_holder_cuboid: {},
      resize_place_holder_cuboid: jest.fn(),
      remove_placeholder_cuboid: jest.fn()
    }
    controller.draw_mode = true;
    controller.currently_drawing_instance = true;
    let spy = jest.spyOn(controller.plane_normal, 'copy')
    let spy2 = jest.spyOn(controller.plane, 'setFromNormalAndCoplanarPoint')
    let spy3 = jest.spyOn(controller.raycaster, 'setFromCamera')
    let result = controller.get_3d_mouse_position();
    expect(spy).toHaveBeenCalled()
    expect(spy2).toHaveBeenCalled()
    expect(spy3).toHaveBeenCalled()
    expect(result).toBe(controller.mouse_position_3d)

  });

  it("Correctly calls check_hover()", () => {
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    controller.cuboid_drawer_tool = {
      place_holder_cuboid: {},
      resize_place_holder_cuboid: jest.fn(),
      remove_placeholder_cuboid: jest.fn()
    }
    controller.draw_mode = false;
    controller.currently_drawing_instance = true;
    let mockmesh = create_test_mesh();
    mockmesh.userData = {
      instance_index: 1
    }
    controller.instance_list = [
      {},
      {
        mesh: mockmesh
      }
    ]
    controller.raycaster.intersectObjects = () => {
      return [
        {
          object: mockmesh
        }
      ]
    }

    let spy = jest.spyOn(controller.raycaster, 'setFromCamera')
    let spy2 = jest.spyOn(controller.raycaster, 'intersectObjects')
    let spy3 = jest.spyOn(controller.component_ctx, '$emit')
    let spy4 = jest.spyOn(controller.raycaster, 'setFromCamera')
    controller.check_hover();
    expect(spy).toHaveBeenCalled()
    expect(spy2).toHaveBeenCalled()
    expect(spy3).toHaveBeenCalledWith(
      'instance_hovered',
      controller.instance_list[mockmesh.userData.instance_index],
      mockmesh.userData.instance_index
    )
    expect(spy4).toHaveBeenCalled()
    expect(mockmesh.material.opacity).toBe(0.5)
    expect(controller.instance_hovered_index).toBe(mockmesh.userData.instance_index)

  });

  it("Correctly calls animate()", () => {
    renderer.render = jest.fn()
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );


    let spy = jest.spyOn(controller, 'render')
    controller.animate();
    expect(spy).toHaveBeenCalled()

  });

  it("Correctly calls render()", () => {
    renderer.render = jest.fn()
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );


    let spy = jest.spyOn(controller, 'reset_materials')
    let spy2 = jest.spyOn(controller, 'check_hover')
    let spy3 = jest.spyOn(controller.renderer, 'render')
    controller.render();
    expect(spy).toHaveBeenCalled()
    expect(spy2).toHaveBeenCalled()
    expect(spy3).toHaveBeenCalled()

  });

  it("Correctly calls attach_mouse_events()", () => {
    renderer.render = jest.fn()
    container.addEventListener = jest.fn()
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );


    let spy = jest.spyOn(controller.container, 'addEventListener')
    controller.attach_mouse_events();
    expect(spy).toHaveBeenNthCalledWith(1, 'mousemove', controller.binded_funcs.on_mouse_move, false)
    expect(spy).toHaveBeenNthCalledWith(2, 'click', controller.binded_funcs.on_mouse_click)
    expect(spy).toHaveBeenNthCalledWith(3, 'dblclick', controller.binded_funcs.on_mouse_double_click)
  });

  it("Correctly calls detach_mouse_events()", () => {
    renderer.render = jest.fn()
    container.addEventListener = jest.fn()
    container.removeEventListener = jest.fn()
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );


    let spy = jest.spyOn(controller.container, 'removeEventListener')
    controller.attach_mouse_events();
    controller.detach_mouse_events();
    expect(spy).toHaveBeenNthCalledWith(1, 'mousemove', controller.binded_funcs.on_mouse_move)
    expect(spy).toHaveBeenNthCalledWith(2, 'click', controller.binded_funcs.on_mouse_click)
    expect(spy).toHaveBeenNthCalledWith(3, 'dblclick', controller.binded_funcs.on_mouse_double_click)
  });

  it("Correctly calls set_current_label_file()", () => {
    renderer.render = jest.fn()
    container.addEventListener = jest.fn()
    container.removeEventListener = jest.fn()
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );

    let label_file = {
      id: 'test'
    }
    let spy = jest.spyOn(controller.container, 'removeEventListener')
    controller.set_current_label_file(label_file);
    expect(controller.label_file).toBe(label_file)
  });

  it("Correctly calls remove_from_scene()", () => {
    renderer.render = jest.fn()
    container.addEventListener = jest.fn()
    container.removeEventListener = jest.fn()
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );

    let object = new THREE.Object3D();
    let spy = jest.spyOn(object, 'removeFromParent')
    controller.remove_from_scene(object);
    expect(spy).toHaveBeenCalled()
  });

  it("Correctly calls set_draw_mode()", () => {
    renderer.render = jest.fn()
    container.addEventListener = jest.fn()
    container.removeEventListener = jest.fn()
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    controller.draw_mode = true;
    controller.object_transform_controls = {};
    controller.currently_drawing_instance = {};
    controller.detach_controls_from_mesh = jest.fn();
    controller.cuboid_drawer_tool = {
      remove_placeholder_cuboid: jest.fn(),
    };
    controller.selected_instance = {};

    let object = new THREE.Object3D();
    let spy = jest.spyOn(controller, 'detach_controls_from_mesh')
    let spy2 = jest.spyOn(controller, 'remove_from_scene')
    let spy3 = jest.spyOn(controller.cuboid_drawer_tool, 'remove_placeholder_cuboid')
    controller.set_draw_mode(false);
    expect(spy).toHaveBeenCalled()
    expect(spy2).toHaveBeenCalled()
    expect(spy3).toHaveBeenCalled()
    expect(controller.currently_drawing_instance).toBe(false)
    expect(controller.currently_drawing_instance).toBe(false)
  });

  it("Correctly calls deselect_instance()", () => {
    renderer.render = jest.fn()
    container.addEventListener = jest.fn()
    container.removeEventListener = jest.fn()
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    controller.selected_instance = {
      remove_edges: jest.fn()
    };
    controller.detach_controls_from_mesh = jest.fn();
    let spy = jest.spyOn(controller.selected_instance, 'remove_edges')
    let spy2 = jest.spyOn(controller, 'detach_controls_from_mesh')
    controller.deselect_instance(false);
    expect(spy).toHaveBeenCalled()
    expect(spy2).toHaveBeenCalled()
    expect(controller.selected_instance).toBe(null)
    expect(controller.selected_instance_index).toBe(null)
  });

  it("Correctly calls select_instance()", () => {
    renderer.render = jest.fn()
    container.addEventListener = jest.fn()
    container.removeEventListener = jest.fn()
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    let instance = {
      highlight_edges: jest.fn(),
      selected: false,
      status: null
    }
    controller.attach_transform_controls_to_mesh = jest.fn();
    let spy = jest.spyOn(controller, 'attach_transform_controls_to_mesh')
    let spy2 = jest.spyOn(instance, 'highlight_edges')
    let spy3 = jest.spyOn(Vue, 'set')
    let spy4 = jest.spyOn(controller.component_ctx, '$emit')
    controller.select_instance(instance, 0);
    expect(spy).toHaveBeenCalled()
    expect(spy2).toHaveBeenCalled()
    expect(spy3).toHaveBeenCalled()
    expect(spy4).toHaveBeenNthCalledWith(1, 'instance_selected', instance, 0)
    expect(instance.selected).toBe(true)
    expect(instance.status).toBe('updated')
    expect(controller.selected_instance).toBe(instance)
    expect(controller.selected_instance_index).toBe(0)
  });

  it("Correctly calls on_click_edit_mode()", () => {
    renderer.render = jest.fn()
    container.addEventListener = jest.fn()
    container.removeEventListener = jest.fn()
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    let instance = {
      highlight_edges: jest.fn(),
      selected: false,
      status: null
    }
    controller.attach_transform_controls_to_mesh = jest.fn();
    controller.select_instance = jest.fn();
    controller.deselect_instance = jest.fn();

    let mockmesh = create_test_mesh();

    mockmesh.userData.instance_index = 0;
    controller.instance_list = [
      {
        mesh: mockmesh,
      }
    ];
    controller.raycaster.intersectObjects = () => {
      return [
        {
          object: mockmesh
        }
      ]
    }
    let spy = jest.spyOn(controller.raycaster, 'setFromCamera')
    let spy2 = jest.spyOn(controller, 'deselect_instance')
    let spy3 = jest.spyOn(controller, 'select_instance')
    controller.on_click_edit_mode(instance, 0);
    expect(spy).toHaveBeenCalled()
    expect(spy2).toHaveBeenCalled()
    expect(spy3).toHaveBeenCalled()
  });

  it("Correctly calls add_mesh_user_data_to_instance()", () => {
    renderer.render = jest.fn()
    container.addEventListener = jest.fn()
    container.removeEventListener = jest.fn()
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    let instance = {
      mesh: new THREE.Mesh(),
      highlight_edges: jest.fn(),
      selected: false,
      status: null
    }
    controller.label_file = {
      colour: {
        hex: 'test'
      }
    }
    controller.add_mesh_user_data_to_instance(instance, 0);
    expect(instance.mesh.userData.instance_index).toBe(0)
    expect(instance.mesh.userData.color).toBe(controller.label_file.colour.hex)
  });

  it("Correctly calls add_cube_to_instance_list()", () => {
    renderer.render = jest.fn()
    container.addEventListener = jest.fn()
    container.removeEventListener = jest.fn()
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    let mockmesh = create_test_mesh();
    controller.label_file = {
      colour: {
        hex: 'test'
      }
    }
    controller.add_mesh_user_data_to_instance = jest.fn();
    let spy = jest.spyOn(controller, 'add_mesh_user_data_to_instance')
    controller.add_cube_to_instance_list(mockmesh);
    expect(controller.instance_list.length).toBe(1)
    expect(spy).toHaveBeenCalled()
  });

  it("Correctly calls start_render()", () => {
    renderer.render = jest.fn()
    container.addEventListener = jest.fn()
    container.removeEventListener = jest.fn()
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    controller.add_mesh_user_data_to_instance = jest.fn();
    let spy = jest.spyOn(controller, 'animate')
    controller.start_render();
    expect(spy).toHaveBeenCalled()
  });

  it("Correctly calls add_orbit_controls()", () => {
    renderer.render = jest.fn()
    renderer.domElement = document.createElement('canvas')
    container.addEventListener = jest.fn()
    container.removeEventListener = jest.fn()
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    controller.add_orbit_controls_events = jest.fn();
    let spy = jest.spyOn(controller, 'add_orbit_controls_events')
    controller.add_orbit_controls();
    expect(controller.controls_orbit).toBeInstanceOf(OrbitControls)
    expect(spy).toHaveBeenCalled();
  });

  it("Correctly calls add_orbit_controls_events()", () => {
    renderer.render = jest.fn()
    renderer.domElement = document.createElement('canvas')
    container.addEventListener = jest.fn()
    container.removeEventListener = jest.fn()
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    controller.controls_orbit = {
      listenToKeyEvents: jest.fn(),
      enabled: false
    }
    let spy = jest.spyOn(controller.controls_orbit, 'listenToKeyEvents')
    controller.add_orbit_controls_events();
    expect(controller.controls_orbit).toBeDefined();
    expect(controller.controls_orbit.enabled).toBe(true);
    expect(spy).toHaveBeenCalled();
  });

  it("Correctly calls remove_orbit_controls_events()", () => {
    renderer.render = jest.fn()
    renderer.domElement = document.createElement('canvas')
    container.addEventListener = jest.fn()
    container.removeEventListener = jest.fn()
    controller = new AnnotationScene3D(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    controller.controls_orbit = {
      listenToKeyEvents: jest.fn(),
      enabled: true
    }
    let spy = jest.spyOn(controller.controls_orbit, 'listenToKeyEvents')
    controller.remove_orbit_controls_events();
    expect(controller.controls_orbit.enabled).toBe(false);
  });

  it("Correctly calls add_transform_controls()", () => {
    renderer.render = jest.fn()
    renderer.domElement = document.createElement('canvas')
    container.addEventListener = jest.fn()
    container.removeEventListener = jest.fn()
    controller = new AnnotationScene3D(
      scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    expect(controller.object_transform_controls).toBe(undefined);
    controller.add_transform_controls();
    expect(controller.object_transform_controls).toBeDefined();
  });

  it("Correctly calls attach_transform_controls_to_mesh()", () => {
    renderer.render = jest.fn()
    renderer.domElement = document.createElement('canvas')
    container.addEventListener = jest.fn()
    container.removeEventListener = jest.fn()
    controller = new AnnotationScene3D(
      scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    let mockmesh = create_test_mesh();
    controller.object_transform_controls = {
      attach_to_mesh: jest.fn()
    }
    controller.attach_transform_controls_to_mesh(mockmesh);
    let spy = jest.spyOn(controller.object_transform_controls, 'attach_to_mesh')
    expect(spy).toHaveBeenCalledWith(mockmesh);
  });

  it("Correctly calls detach_controls_from_mesh()", () => {
    renderer.render = jest.fn()
    renderer.domElement = document.createElement('canvas')
    container.addEventListener = jest.fn()
    container.removeEventListener = jest.fn()
    controller = new AnnotationScene3D(
      scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    let mockmesh = create_test_mesh();
    controller.object_transform_controls = {
      detach_controls: jest.fn()
    }
    controller.detach_controls_from_mesh();
    let spy = jest.spyOn(controller.object_transform_controls, 'detach_controls')
    expect(spy).toHaveBeenCalledWith();
  });


  it("Correctly calls add_mesh_to_scene()", () => {
    renderer.render = jest.fn()
    renderer.domElement = document.createElement('canvas')
    container.addEventListener = jest.fn()
    container.removeEventListener = jest.fn()
    controller = new AnnotationScene3D(
      scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    let mockmesh = create_test_mesh();
    controller.object_transform_controls = {
      detach_controls: jest.fn()
    }
    controller.center_camera_to_mesh = jest.fn();
    let spy = jest.spyOn(controller.scene, 'add')
    let spy2 = jest.spyOn(controller, 'center_camera_to_mesh')

    controller.add_mesh_to_scene(mockmesh, true);

    expect(spy).toHaveBeenCalledWith(mockmesh);
    expect(spy2).toHaveBeenCalledWith(mockmesh);
  });


  it("Correctly calls center_camera_to_mesh()", () => {
    renderer.render = jest.fn()
    renderer.domElement = document.createElement('canvas')
    container.addEventListener = jest.fn()
    container.removeEventListener = jest.fn()
    controller = new AnnotationScene3D(
      scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    let mockmesh = create_test_mesh();
    mockmesh.geometry.computeBoundingSphere()
    controller.object_transform_controls = {
      detach_controls: jest.fn()
    }
    controller.controls_orbit = {
      target: {
        copy: jest.fn(),

      },
      update: jest.fn()
    }
    let spy = jest.spyOn(controller.camera, 'getEffectiveFOV')
    let spy2 = jest.spyOn(controller.camera, 'getWorldDirection')
    let spy3 = jest.spyOn(mockmesh, 'localToWorld')
    let spy4 = jest.spyOn(controller.camera.position, 'copy')

    controller.center_camera_to_mesh(mockmesh, 'x');

    expect(spy).toHaveBeenCalled();
    expect(spy2).toHaveBeenCalled();
    expect(spy3).toHaveBeenCalled();
    expect(spy4).toHaveBeenCalled();

  });



});
