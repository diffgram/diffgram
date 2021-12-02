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


window.alert = jest.fn();

describe("Test canvas_3d.vue", () => {
  let options;
  let wrapper: Wrapper<Vue>;
  beforeEach(() => {

  });

  it("Correctly creates a CuboidDrawerTool() object", () => {
    let ctx = {loading_pcd: false, percentage: 1}
    let camera = mocked(THREE.PerspectiveCamera, true) as unknown as THREE.PerspectiveCamera;
    let scene_controller = mocked(SceneController3D, true) as unknown as SceneController3D;
    let domeElement = document.createElement('canvas');
    let scene = scene_controller.scene;
    let render_function = jest.fn();
    let drag_function = jest.fn();
    let layer_number = 1;
    let spyAdd = jest.spyOn(scene, 'add')
    let controls = new ObjectTransformControls(camera,
      scene_controller,
      domeElement,
      scene,
      render_function,
      drag_function,
      layer_number);
    expect(controls.controls_transform).toBeDefined();
    expect(controls.scene_controller).toBe(scene_controller);
    expect(spyAdd).toHaveBeenCalledWith(controls.controls_transform);

  });

  it("Correctly creates a load_pcd_from_url() object", async () => {
    let ctx = {loading_pcd: false, percentage: 1}
    let loader = new ObjectTransformControls(ctx);
    let pcd_loader = loader.pcd_loader;


    let spy = jest.spyOn(pcd_loader, 'load')
    try{
      let mesh = await loader.load_pcd_from_url('loca.pcd') as THREE.Mesh;
    }
    catch (e) {

    }

    expect(spy).toHaveBeenCalled()
  });

});
