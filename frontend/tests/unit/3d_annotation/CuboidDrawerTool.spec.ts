import Vuex from "vuex";
import {shallowMount, createLocalVue, Wrapper} from "@vue/test-utils";
import CuboidDrawerTool from "../../../src/components/3d_annotation/CuboidDrawerTool";
import * as THREE from "three";
import {WEBGL} from "../../../src/components/3d_annotation/WebGL";
import mock = jest.mock;
import AnnotationScene3D from "../../../src/components/3d_annotation/AnnotationScene3D";
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
    let scene_controller = mocked(AnnotationScene3D, true);
    let cuboid_drawer_tools = new CuboidDrawerTool(scene_controller);
    expect(cuboid_drawer_tools.mouse_position_3d_initial_draw).toMatchObject(new THREE.Vector3())
    expect(cuboid_drawer_tools.place_holder_cuboid).toBe(null)
    expect(cuboid_drawer_tools.scene_controller).toBe(scene_controller)
  });

  it("Correctly calls create_mesh_from_instance_data()", () => {
    let scene_controller = mocked(AnnotationScene3D, true);
    let cuboid_drawer_tools = new CuboidDrawerTool(scene_controller);
    let mock_instance = mocked(Cuboid3DInstance, true) as unknown as Cuboid3DInstance;
    mock_instance.label_file = {
      id: 1,
      label: null,
      colour: {
        hex: '#ffffff'
      }
    }
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
    expect(geometry.parameters.width).toBe(mock_instance.dimensions_3d.width)
    expect(geometry.parameters.height).toBe(mock_instance.dimensions_3d.height)
    expect(geometry.parameters.depth).toBe(mock_instance.dimensions_3d.depth)
    expect(result.position.x).toBe(mock_instance.position_3d.x)
    expect(result.position.y).toBe(mock_instance.position_3d.y)
    expect(result.position.z).toBe(mock_instance.position_3d.z)
  });

  it("Correctly calls remove_placeholder_cuboid()", () => {
    let scene_controller = mocked(AnnotationScene3D, true);
    let cuboid_drawer_tools = new CuboidDrawerTool(scene_controller);
    let mock_instance = mocked(Cuboid3DInstance, true) as unknown as Cuboid3DInstance;
    mock_instance.label_file = {
      id: 1,
      label: null,
      colour: {
        hex: '#ffffff'
      }
    }
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

    cuboid_drawer_tools.remove_placeholder_cuboid();
    expect(cuboid_drawer_tools.place_holder_cuboid).toBe(null);
  });

  it("Correctly calls resize_place_holder_cuboid()", () => {
    let scene_controller = mocked(AnnotationScene3D, true) as unknown as AnnotationScene3D;
    let cuboid_drawer_tools = new CuboidDrawerTool(scene_controller);
    let mock_instance = mocked(Cuboid3DInstance, true) as unknown as Cuboid3DInstance;

    scene_controller.mouse_position_3d = new THREE.Vector3(1, 2, 3);
    scene_controller.render = jest.fn();
    cuboid_drawer_tools.mouse_position_3d_initial_draw = new THREE.Vector3(1, 2, 3);

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
    cuboid_drawer_tools.place_holder_cuboid = result;

    mock_instance.label_file = {
      id: 1,
      label: null,
      colour: {
        hex: '#ffffff'
      }
    }
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
    let mouse_position_3d = scene_controller.mouse_position_3d;
    let xSize = mouse_position_3d.x - cuboid_drawer_tools.mouse_position_3d_initial_draw.x;
    let ySize = mouse_position_3d.y - cuboid_drawer_tools.mouse_position_3d_initial_draw.y;
    let zSize = Math.max(xSize, ySize);

    let geometry = cuboid_drawer_tools.place_holder_cuboid.geometry as THREE.BoxGeometry;

    let scaleFactorX = xSize / geometry.parameters.width;
    let scaleFactorY = ySize / geometry.parameters.height;
    let scaleFactorZ = zSize / geometry.parameters.depth;

    cuboid_drawer_tools.resize_place_holder_cuboid();
    expect(cuboid_drawer_tools.place_holder_cuboid.scale.x).toBe(scaleFactorX);
    expect(cuboid_drawer_tools.place_holder_cuboid.scale.y).toBe(scaleFactorY);
    expect(cuboid_drawer_tools.place_holder_cuboid.scale.z).toBe(scaleFactorZ);

  });

});
