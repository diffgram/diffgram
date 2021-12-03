import Vuex from "vuex";
import Vue from "vue";
import * as THREE from "three";
import {shallowMount, createLocalVue, Wrapper} from "@vue/test-utils";
import ObjectTransformControls from "../../../src/components/3d_annotation/ObjectTransformControls";
import SceneController3D from "../../../src/components/3d_annotation/SceneController3D";
import axios from "axios";
import {mocked} from 'ts-jest/utils'
import {load} from "mime";

axios.defaults.adapter = require('axios/lib/adapters/http')

jest.mock("three/src/renderers/WebGLRenderer"); // this happens automatically with automocking
const localVue = createLocalVue();
localVue.use(Vuex);

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
    point_cloud_mesh = mocked(THREE.Mesh, true) as unknown as THREE.Mesh;;
    renderer = {
      setPixelRatio: jest.fn()
    };
    container = document.createElement('setPixelRatio');
    layer_number = 1;


  });

  it("Correctly creates a SceneController3D() object", () => {
    let spy = jest.spyOn(renderer, 'setPixelRatio')
    let spy2 = jest.spyOn(scene, 'add')

    controller = new SceneController3D(scene,
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


    controller = new SceneController3D(scene,
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
    controller = new SceneController3D(scene,
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
    controller = new SceneController3D(scene,
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
    controller = new SceneController3D(scene,
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


});
