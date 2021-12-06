import Vuex from "vuex";
import Vue from "vue";
import * as THREE from "three";
import {shallowMount, createLocalVue, Wrapper} from "@vue/test-utils";
import ObjectTransformControls from "../../../src/components/3d_annotation/ObjectTransformControls";
import AnnotationScene3DOrtographicView from "../../../src/components/3d_annotation/AnnotationScene3DOrtographicView";
import axios from "axios";
import {mocked} from 'ts-jest/utils'
import {load} from "mime";
import mock = jest.mock;
import {OrbitControls} from "../../../src/components/3d_annotation/OrbitControls";
import {getCenterPoint} from "../../../src/components/3d_annotation/utils_3d";

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
    point_cloud_mesh = mocked(THREE.Mesh, true) as unknown as THREE.Mesh;
    ;
    renderer = {
      setPixelRatio: jest.fn()
    };
    container = document.createElement('setPixelRatio');
    layer_number = 1;


  });

  it("Correctly creates a AnnotationScene3DOrtographicView() object", () => {
    let spy = jest.spyOn(renderer, 'setPixelRatio')
    let spy2 = jest.spyOn(scene, 'add')
    let spy3 = jest.spyOn(camera.layers, 'disable')

    controller = new AnnotationScene3DOrtographicView(scene,
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
    expect(spy3).toHaveBeenCalledTimes(1)
  });

  it("Correctly calls add_orbit_controls()", () => {
    renderer.render = jest.fn()
    renderer.domElement = document.createElement('canvas')
    controller = new AnnotationScene3DOrtographicView(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );

    controller.controls_orbit = {

    }
    controller.controls_orbit.enableRotate = true;
    controller.controls_orbit.update = jest.fn();

    let spy = jest.spyOn(controller, 'add_orbit_controls')
    let spy2 = jest.spyOn(controller.controls_orbit, 'update')
    controller.add_orbit_controls()
    expect(spy).toHaveBeenCalledTimes(1)
    expect(controller.controls_orbit.enableRotate).toBe(false)
  });


  it("Correctly calls add_transform_controls()", () => {
    renderer.render = jest.fn()
    renderer.domElement = document.createElement('canvas')
    controller = new AnnotationScene3DOrtographicView(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );

    controller.add_transform_controls()
  });

  it("Correctly calls on_click_edit_mode()", () => {
    renderer.render = jest.fn()
    renderer.domElement = document.createElement('canvas')
    controller = new AnnotationScene3DOrtographicView(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );

    controller.on_click_edit_mode()
  });

  it("Correctly calls attach_transform_controls_to_mesh()", () => {
    renderer.render = jest.fn()
    renderer.domElement = document.createElement('canvas')
    controller = new AnnotationScene3DOrtographicView(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );

    controller.attach_transform_controls_to_mesh()
  });

  it("Correctly calls center_camera_to_mesh()", () => {
    renderer.render = jest.fn()
    renderer.domElement = document.createElement('canvas')
    controller = new AnnotationScene3DOrtographicView(scene,
      camera,
      renderer,
      container,
      component_ctx,
      instance_list,
      controls_panning_speed,
      point_cloud_mesh
    );
    let frustrum_height;
    let mockmesh = create_test_mesh();
    let center = getCenterPoint(mockmesh);
    var helper_bbox = new THREE.BoxHelper(mockmesh);
    helper_bbox.update();
    var aspect = controller.clientWidth / controller.clientHeight;
    var bbox_radius = helper_bbox.geometry.boundingSphere.radius;
    if(aspect > 1){
      frustrum_height = 2 * bbox_radius;
    }
    else{
      frustrum_height = 2 * bbox_radius / aspect;
    }
    let spy = jest.spyOn(controller.camera, 'lookAt')
    controller.add_mesh_to_scene(mockmesh, false);
    controller.center_camera_to_mesh(mockmesh);
    expect(controller.camera.position.x).toBe(center.x - 20);
    expect(controller.camera.position.y).toBe(center.y);
    expect(controller.camera.left).toBe(- frustrum_height * aspect / 2);
    expect(controller.camera.right).toBe(frustrum_height * aspect / 2);
    expect(controller.camera.top).toBe(frustrum_height / 2);
    expect(controller.camera.bottom).toBe(frustrum_height / 2);
    expect(spy).toHaveBeenCalled();
  });


});
