import Vuex from "vuex";
import Vue from "vue";
import * as THREE from "three";
import {shallowMount, createLocalVue, Wrapper} from "@vue/test-utils";
import ObjectTransformControls from "../../../src/components/3d_annotation/ObjectTransformControls";
import AnnotationScene3D from "../../../src/components/3d_annotation/AnnotationScene3D";
import axios from "axios";
import {mocked} from 'ts-jest/utils'
import {load} from "mime";
axios.defaults.adapter = require('axios/lib/adapters/http')

jest.mock("three/src/renderers/WebGLRenderer"); // this happens automatically with automocking
const localVue = createLocalVue();
localVue.use(Vuex);


window.alert = jest.fn();

describe("Test ObjectTransformControls.spec.ts", () => {
  let controls;
  let wrapper: Wrapper<Vue>;
  beforeEach(() => {
    let ctx = {loading_pcd: false, percentage: 1}
    let camera = mocked(THREE.PerspectiveCamera, true) as unknown as THREE.PerspectiveCamera;
    let scene_controller = mocked(AnnotationScene3D, true) as unknown as AnnotationScene3D;
    let domeElement = document.createElement('canvas');
    scene_controller.scene = new THREE.Scene();
    let scene = scene_controller.scene;
    let render_function = jest.fn();
    let drag_function = jest.fn();
    let layer_number = 1;
    let spyAdd = jest.spyOn(scene, 'add')
    controls = new ObjectTransformControls(camera,
      scene_controller,
      domeElement,
      scene,
      render_function,
      drag_function,
      layer_number);
  });

  it("Correctly creates a ObjectTransformControls() object", () => {
    let ctx = new Vue();
    let camera = mocked(THREE.PerspectiveCamera, true) as unknown as THREE.PerspectiveCamera;
    let scene_controller = mocked(AnnotationScene3D, true) as unknown as AnnotationScene3D;
    let domeElement = document.createElement('canvas');
    scene_controller.scene = new THREE.Scene();
    scene_controller.component_ctx = ctx;
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

  it("Correctly calls on_mesh_changed()", () => {

    let event = {
      target:{
        object:{
          userData:{
            instance_index: 1
          }
        }
      }
    }
    controls.scene_controller.instance_list = [
      {},
      {
        mesh:{
          position: {
            copy: jest.fn()
          },
          rotation: {
            copy: jest.fn()
          },
          scale: {
            copy: jest.fn()
          }

        },
        helper_lines:{
          position: {
            copy: jest.fn()
          },
          rotation: {
            copy: jest.fn()
          },
          scale: {
            copy: jest.fn()
          }
        },
        update_spacial_data: jest.fn()
      }
    ]
    let spy1 = jest.spyOn(controls.scene_controller.instance_list[1], 'update_spacial_data')
    let spy2 = jest.spyOn(controls.scene_controller.instance_list[1].helper_lines.position, 'copy')
    let spy3 = jest.spyOn(controls.scene_controller.instance_list[1].helper_lines.rotation, 'copy')
    let spy4 = jest.spyOn(controls.scene_controller.instance_list[1].helper_lines.scale, 'copy')
    let spy5 = jest.spyOn(controls.scene_controller.component_ctx, '$emit')
    controls.on_mesh_changed(event);
    expect(spy1).toHaveBeenCalled();
    expect(spy2).toHaveBeenCalled();
    expect(spy3).toHaveBeenCalled();
    expect(spy4).toHaveBeenCalled();
    expect(spy5).toHaveBeenCalledWith('instance_updated', controls.scene_controller.instance_list[1]);

  });

  it("Correctly calls on_key_down_object_transform()", () => {

    let event = {
      keyCode: 81
    }
    controls.controls_transform = {
      setSpace: jest.fn(),
      setTranslationSnap: jest.fn(),
      setRotationSnap: jest.fn(),
      setMode: jest.fn(),
      setSize: jest.fn(),
      setScaleSnap: jest.fn(),
      detach: jest.fn(),
      object: {},
      showX: true,
      showY: true,
      showZ: true,
      enabled: true,
      mode: 'translate'
    }
    let spy = jest.spyOn(controls.controls_transform, 'setSpace')
    controls.on_key_down_object_transform(event);
    expect(spy).toHaveBeenCalled();

    let spy2 = jest.spyOn(controls.controls_transform, 'setTranslationSnap')
    let spy3 = jest.spyOn(controls.controls_transform, 'setRotationSnap')
    let spy4 = jest.spyOn(controls.controls_transform, 'setScaleSnap')
    event.keyCode = 16
    controls.on_key_down_object_transform(event);
    expect(spy2).toHaveBeenCalled();
    expect(spy3).toHaveBeenCalled();
    expect(spy4).toHaveBeenCalled();

    spy = jest.spyOn(controls.controls_transform, 'setMode')
    event.keyCode = 84
    controls.on_key_down_object_transform(event);
    expect(spy).toHaveBeenCalled();

    spy = jest.spyOn(controls.controls_transform, 'setSize')
    event.keyCode = 107
    controls.on_key_down_object_transform(event);
    expect(spy).toHaveBeenCalled();

    spy = jest.spyOn(controls.controls_transform, 'setSize')
    event.keyCode = 109
    controls.on_key_down_object_transform(event);
    expect(spy).toHaveBeenCalled();

    event.keyCode = 88
    controls.on_key_down_object_transform(event);
    expect(controls.controls_transform.showX ).toBe(false);

    event.keyCode = 89
    controls.on_key_down_object_transform(event);
    expect(controls.controls_transform.showY ).toBe(false);

    event.keyCode = 90
    controls.on_key_down_object_transform(event);
    expect(controls.controls_transform.showZ ).toBe(false);

    event.keyCode = 32
    controls.on_key_down_object_transform(event);
    expect(controls.controls_transform.enabled ).toBe(false);

    spy = jest.spyOn(controls.controls_transform, 'detach')
    event.keyCode = 27
    controls.on_key_down_object_transform(event);
    expect(spy).toHaveBeenCalled();

  });

  it("Correctly calls add_hotkeys_for_transform_controls()", () => {

    let spy = jest.spyOn(window, 'addEventListener')
    controls.add_hotkeys_for_transform_controls();
    expect(spy).toHaveBeenCalled();

  });

  it("Correctly calls remove_hotkeys_for_transform_controls()", () => {

    let spy = jest.spyOn(window, 'removeEventListener')
    controls.remove_hotkeys_for_transform_controls();
    expect(spy).toHaveBeenCalled();

  });

  it("Correctly calls detach_controls()", () => {
    controls.scene_controller.render = jest.fn();
    controls.controls_transform = {
      setSpace: jest.fn(),
      setTranslationSnap: jest.fn(),
      setRotationSnap: jest.fn(),
      setMode: jest.fn(),
      setSize: jest.fn(),
      setScaleSnap: jest.fn(),
      removeEventListener: jest.fn(),
      detach: jest.fn(),
      object: {},
      showX: true,
      showY: true,
      showZ: true,
      enabled: true,
      mode: 'translate'
    }
    let spy = jest.spyOn(controls.controls_transform, 'detach')
    let spy2 = jest.spyOn(controls.controls_transform, 'removeEventListener')
    controls.detach_controls();
    expect(spy).toHaveBeenCalled();
    expect(spy2).toHaveBeenCalled();

  });

  it("Correctly calls attach_to_mesh()", () => {
    controls.scene_controller.render = jest.fn();
    controls.controls_transform = {
      addEventListener: jest.fn(),
      detach: jest.fn(),
      attach: jest.fn(),
    }
    let spy = jest.spyOn(controls.controls_transform, 'attach')
    let spy2 = jest.spyOn(controls.controls_transform, 'addEventListener')
    let spy3 = jest.spyOn(controls.scene_controller, 'render')
    controls.attach_to_mesh();
    expect(spy).toHaveBeenCalled();
    expect(spy2).toHaveBeenCalled();
    expect(spy3).toHaveBeenCalled();

  });

});
