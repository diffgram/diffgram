import Vuex from "vuex";
import {shallowMount, createLocalVue, Wrapper} from "@vue/test-utils";
import CuboidDrawerTool from "../../../src/components/3d_annotation/CuboidDrawerTool";
import * as THREE from "three";
import {WEBGL} from "../../../src/components/3d_annotation/WebGL";
import mock = jest.mock;
import SceneController3D from "../../../src/components/3d_annotation/SceneController3D";
import Cuboid3DInstance from "../../../src/components/vue_canvas/instances/Cuboid3DInstance"
import {mocked} from 'ts-jest/utils'

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
    let scene_controller = mocked(SceneController3D, true);
    let cuboid_drawer_tools = new CuboidDrawerTool(scene_controller);
    expect(cuboid_drawer_tools.mouse_position_3d_initial_draw).toMatchObject(new THREE.Vector3())
    expect(cuboid_drawer_tools.place_holder_cuboid).toBe(null)
    expect(cuboid_drawer_tools.scene_controller).toMatchObject(scene_controller)
  });

  it("Correctly calls create_mesh_from_instance_data()", () => {
    let scene_controller = mocked(SceneController3D, true);
    let cuboid_drawer_tools = new CuboidDrawerTool(scene_controller);
    let mock_instance = mocked(Cuboid3DInstance, true) as unknown as Cuboid3DInstance;
    mock_instance.dimensions_3d = {
      width: 1,
      height: 2,
      depth: 3,
    };
    mock_instance.position_3d = {
      x: 1,
      y: 2,
      z: 3
    }

    let result = cuboid_drawer_tools.create_mesh_from_instance_data(mock_instance)
    let geometry = result.geometry as THREE.BoxGeometry;
    expect(result).toBeDefined()
    expect(geometry.parameters.width).toMatchObject(mock_instance.dimensions_3d.width)
    expect(geometry.parameters.height).toMatchObject(mock_instance.dimensions_3d.height)
    expect(geometry.parameters.depth).toMatchObject(mock_instance.dimensions_3d.depth)
    expect(result.position.x).toBe(mock_instance.position_3d.x)
    expect(result.position.y).toBe(mock_instance.position_3d.y)
    expect(result.position.z).toBe(mock_instance.position_3d.z)
  });


});
