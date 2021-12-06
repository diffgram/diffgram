import Vuex from "vuex";
import {shallowMount, createLocalVue, Wrapper} from "@vue/test-utils";
import sensor_fusion_editor from "../../../src/components/3d_annotation/sensor_fusion_editor";
import FileLoader3DPointClouds from "../../../src/components/3d_annotation/FileLoader3DPointClouds";
import * as instanceServices from '../../../src/services/instanceServices';
import * as instance_utils from "../../../src/utils/instance_utils"
import {create_test_mesh} from './3d_mocks'
import * as THREE from 'three';
import axios from "axios";

jest.mock("three/src/renderers/WebGLRenderer"); // this happens automatically with automocking
jest.mock("../../../src/components/3d_annotation/FileLoader3DPointClouds", () => {
    return jest.fn().mockImplementation(() => {
      return {
        load_pcd_from_url: async () => ({
          material: {},
          geometry: {}
        })
      };
    })
  }
);
jest.mock("../../../src/components/annotation/commands/update_instance_command"); // this happens automatically with automocking
const localVue = createLocalVue();
localVue.use(Vuex);
axios.defaults.adapter = require('axios/lib/adapters/http')

window.alert = jest.fn();
let options, wrapper, actions, store;
describe("Test sensor_fusion_editor.vue", () => {


  beforeEach(() => {
    actions = {
      actionClick: jest.fn(),
      actionInput: jest.fn()
    }
    store = new Vuex.Store({
      actions,
      mutations: {
        'set_user_is_typing_or_menu_open': jest.fn(),
      }
    })
    options = {
      localVue: localVue,
      store: store,
      propsData: {

        view_only_mode: false
      },
      mocks: {}
    };
  });

  it("Tests if sensor_fusion_editor mounts successfully", () => {
    wrapper = shallowMount(sensor_fusion_editor, options);
    expect(wrapper.html().includes(`id="3d-editor-container"`)).toBeTruthy();
  });

  it("correctly calls delete_instance()", () => {
    wrapper = shallowMount(sensor_fusion_editor, options);
    wrapper.setData({
      instance_list: [
        {
          selected: true
        },
        {
          selected: true
        },
        {
          selected: true
        }
      ]
    })
    wrapper.vm.instance_update = jest.fn();
    let spy1 = jest.spyOn(wrapper.vm, 'instance_update');
    wrapper.vm.delete_instance()

    expect(spy1).toHaveBeenCalledTimes(3)
  });

  it("correctly calls create_update_command()", () => {
    wrapper = shallowMount(sensor_fusion_editor, options);
    wrapper.setData({
      instance_list: [
        {
          selected: true
        },
        {
          selected: true
        },
        {
          selected: true
        }
      ],
      main_canvas_height: 100,
      main_canvas_width: 100,
      point_cloud_mesh: create_test_mesh(),
    })
    wrapper.vm.instance_update = jest.fn();
    wrapper.vm.$refs.main_3d_canvas = {
      scene_controller: {}
    };
    wrapper.vm.command_manager = {
      executeCommand: jest.fn(),
    }
    let spy1 = jest.spyOn(wrapper.vm.command_manager, 'executeCommand');
    wrapper.vm.create_update_command()

    expect(wrapper.vm.command_manager).toBeDefined()
    expect(spy1).toHaveBeenCalled()
  });

  it("correctly calls instance_update()", () => {
    wrapper = shallowMount(sensor_fusion_editor, options);
    wrapper.setData({
      instance_list: [
        {
          index: 0,
          id: 1,
          selected: true,
          toggle_occluded: jest.fn(),
        },
        {
          selected: true
        },
        {
          selected: true
        }
      ],
      main_canvas_height: 100,
      main_canvas_width: 100,
      point_cloud_mesh: create_test_mesh(),
    })
    wrapper.vm.$refs.main_3d_canvas = {
      scene_controller: {}
    };
    wrapper.vm.command_manager = {
      executeCommand: jest.fn(),
    }
    let spy1 = jest.spyOn(wrapper.vm.instance_list[0], 'toggle_occluded');
    wrapper.vm.instance_update({
      mode: 'on_click_update_point_attribute',
      index: 0
    })
    expect(spy1).toHaveBeenCalled()

    let update_mock = {
      mode: 'update_label',
      index: 0,
      payload: {
        test: 'test',
        id: 5788
      }
    }
    wrapper.vm.instance_update(update_mock)
    expect(wrapper.vm.instance_list[0].label_file).toBe(update_mock.payload);
    expect(wrapper.vm.instance_list[0].label_file_id).toBe(update_mock.payload.id);

    let change_sequence = {
      mode: 'change_sequence',
      index: 0,
      sequence: {
        number: 74,
        id: 5788
      }
    }
    wrapper.vm.instance_update(change_sequence)
    expect(wrapper.vm.instance_list[0].sequence_id).toBe(change_sequence.sequence.id);
    expect(wrapper.vm.instance_list[0].number).toBe(change_sequence.sequence.number);


  });

  it("correctly calls instance_update()", () => {
    wrapper = shallowMount(sensor_fusion_editor, options);
    wrapper.setData({
      instance_list: [
        {
          index: 0,
          id: 1,
          selected: true,
          toggle_occluded: jest.fn(),
          draw_on_scene: jest.fn(),
        },
        {
          selected: true
        },
        {
          selected: true
        }
      ],
      main_canvas_height: 100,
      main_canvas_width: 100,
      point_cloud_mesh: create_test_mesh(),
    })
    wrapper.vm.$refs.main_3d_canvas = {
      scene_controller: {
        deselect_instance: jest.fn(),
        remove_from_scene: jest.fn(),
        select_instance: jest.fn()
      }
    };
    wrapper.vm.command_manager = {
      executeCommand: jest.fn(),
    }
    let spy1 = jest.spyOn(wrapper.vm.instance_list[0], 'toggle_occluded');
    wrapper.vm.instance_update({
      mode: 'on_click_update_point_attribute',
      index: 0
    })
    expect(spy1).toHaveBeenCalled()

    let update_mock = {
      mode: 'update_label',
      index: 0,
      payload: {
        test: 'test',
        id: 5788
      }
    }
    wrapper.vm.instance_update(update_mock)
    expect(wrapper.vm.instance_list[0].label_file).toBe(update_mock.payload);
    expect(wrapper.vm.instance_list[0].label_file_id).toBe(update_mock.payload.id);

    let change_sequence = {
      mode: 'change_sequence',
      index: 0,
      sequence: {
        number: 74,
        id: 5788
      }
    }
    wrapper.vm.instance_update(change_sequence)
    expect(wrapper.vm.instance_list[0].sequence_id).toBe(change_sequence.sequence.id);
    expect(wrapper.vm.instance_list[0].number).toBe(change_sequence.sequence.number);

    let delete_payload = {
      mode: 'delete',
      index: 0,
      sequence: {
        number: 74,
        id: 5788
      }
    }
    let spy = jest.spyOn(wrapper.vm.$refs.main_3d_canvas.scene_controller, 'deselect_instance')
    let spy2 = jest.spyOn(wrapper.vm.$refs.main_3d_canvas.scene_controller, 'remove_from_scene')
    wrapper.vm.instance_update(delete_payload)
    expect(wrapper.vm.instance_list[0].soft_delete).toBe(true);
    expect(wrapper.vm.has_changed).toBe(true);
    expect(spy).toHaveBeenCalled();
    expect(spy2).toHaveBeenCalled();

    delete_payload = {
      mode: 'delete_undo',
      index: 0,
      sequence: {
        number: 74,
        id: 5788
      }
    }
    spy = jest.spyOn(wrapper.vm.instance_list[0], 'draw_on_scene')
    spy2 = jest.spyOn(wrapper.vm.$refs.main_3d_canvas.scene_controller, 'select_instance')
    wrapper.vm.instance_update(delete_payload)
    expect(wrapper.vm.instance_list[0].soft_delete).toBe(false);
    expect(wrapper.vm.has_changed).toBe(true);
    expect(spy).toHaveBeenCalled();

    let attribute_change_payload = {
      mode: 'attribute_change',
      index: 0,
      payload: [
        {id: 'group_id_test'},
        {
          test: 2
        }
      ]
    }
    wrapper.vm.instance_update(attribute_change_payload)
    expect(wrapper.vm.instance_list[0].attribute_groups[attribute_change_payload.payload[0].id]).toBe(
      attribute_change_payload.payload[1]
    );

    expect(spy).toHaveBeenCalled();

  });

  it("correctly calls load_pcd()", async () => {
    options.propsData.file = {
      point_cloud: {
        url_signed: 'https://github.com/mrdoob/three.js/raw/master/examples/models/pcd/binary/Zaghetto.pcd'
      },
    }
    wrapper = shallowMount(sensor_fusion_editor, options);
    wrapper.setData({
      instance_list: [
        {
          selected: true
        },
        {
          selected: true
        },
        {
          selected: true
        }
      ],
      main_canvas_height: 100,
      main_canvas_width: 100,
      point_cloud_mesh: create_test_mesh(),
    })
    wrapper.vm.instance_update = jest.fn();
    wrapper.vm.load_instance_list = jest.fn();
    wrapper.vm.$refs.main_3d_canvas = {
      scene_controller: {}
    };
    wrapper.vm.command_manager = {
      executeCommand: jest.fn(),
    }
    let result;
    result = await wrapper.vm.load_pcd('https://github.com/mrdoob/three.js/raw/master/examples/models/pcd/binary/Zaghetto.pcd')

    expect(result).toBeDefined()
    expect(result.material).toBeDefined()
    expect(result.geometry).toBeDefined()
  });

  it("correctly calls add_meshes_to_scene()", async () => {
    options.propsData.file = {
      point_cloud: {
        url_signed: 'https://github.com/mrdoob/three.js/raw/master/examples/models/pcd/binary/Zaghetto.pcd'
      },
    }
    let instance_list = [
      {
        type: 'cuboid_3d',
        selected: true
      },
      {
        type: 'cuboid_3d',
        selected: true
      },
      {
        type: 'cuboid_3d',
        selected: true
      }
    ]
    wrapper = shallowMount(sensor_fusion_editor, options);
    wrapper.setData({
      instance_list: instance_list,
      main_canvas_height: 100,
      main_canvas_width: 100,
      point_cloud_mesh: create_test_mesh(),
    })
    wrapper.vm.instance_update = jest.fn();
    wrapper.vm.load_instance_list = jest.fn();
    wrapper.vm.$refs.main_3d_canvas = {
      scene_controller: {
        add_mesh_to_scene: jest.fn(),
        add_mesh_user_data_to_instance: jest.fn(),

      }
    };
    wrapper.vm.command_manager = {
      executeCommand: jest.fn(),
    }
    let result;


    let spy = jest.spyOn(wrapper.vm.$refs.main_3d_canvas.scene_controller, 'add_mesh_to_scene')
    let spy2 = jest.spyOn(wrapper.vm.$refs.main_3d_canvas.scene_controller, 'add_mesh_user_data_to_instance')
    await wrapper.vm.add_meshes_to_scene(instance_list)

    expect(spy).toHaveBeenCalled()
    expect(spy2).toHaveBeenCalled()
  });


  it("correctly calls load_instance_list()", async () => {
    options.propsData.file = {
      point_cloud: {
        url_signed: 'https://github.com/mrdoob/three.js/raw/master/examples/models/pcd/binary/Zaghetto.pcd'
      },
    }
    let instance_list = [
      {
        type: 'cuboid_3d',
        selected: true
      },
      {
        type: 'cuboid_3d',
        selected: true
      },
      {
        type: 'cuboid_3d',
        selected: true
      }
    ]
    wrapper = shallowMount(sensor_fusion_editor, options);
    wrapper.setData({
      instance_list: instance_list,
      main_canvas_height: 100,
      main_canvas_width: 100,
      point_cloud_mesh: create_test_mesh(),
    })
    wrapper.vm.instance_update = jest.fn();

    wrapper.vm.$refs.main_3d_canvas = {
      scene_controller: {
        add_mesh_to_scene: jest.fn(),
        add_mesh_user_data_to_instance: jest.fn(),

      }
    };
    wrapper.vm.command_manager = {
      executeCommand: jest.fn(),
    }
    let result;

    instanceServices.get_instance_list_from_file = async () => ({file_serialized: {instance_list: []}})
    let spy = jest.spyOn(instanceServices, 'get_instance_list_from_file')
    let spy2 = jest.spyOn(instance_utils, 'create_instance_list_with_class_types')
    let spy3 = jest.spyOn(wrapper.vm, 'add_meshes_to_scene')
    await wrapper.vm.load_instance_list()

    expect(spy).toHaveBeenCalled()
    expect(spy2).toHaveBeenCalled()
    expect(spy3).toHaveBeenCalled()
  });

  it("correctly calls reload_file_data()", async () => {
    options.propsData.file = {
      point_cloud: {
        url_signed: 'https://github.com/mrdoob/three.js/raw/master/examples/models/pcd/binary/Zaghetto.pcd'
      },
    }
    wrapper = shallowMount(sensor_fusion_editor, options);
    wrapper.setData({
      main_canvas_height: 100,
      main_canvas_width: 100,
      point_cloud_mesh: create_test_mesh(),
    })
    wrapper.vm.instance_update = jest.fn();

    wrapper.vm.$refs.main_3d_canvas = {
      destroy_canvas: jest.fn(),
      load_canvas: async () => {},
      scene_controller: {
        add_mesh_to_scene: jest.fn(),
        add_mesh_user_data_to_instance: jest.fn(),

      }
    };
    wrapper.vm.$refs.x_axis_3d_canvas = {
      destroy_canvas: jest.fn()
    };
    wrapper.vm.$refs.y_axis_3d_canvas = {
      destroy_canvas: jest.fn()
    };
    wrapper.vm.$refs.z_axis_3d_canvas = {
      destroy_canvas: jest.fn()
    };
    wrapper.vm.command_manager = {
      executeCommand: jest.fn(),
    }
    wrapper.vm.load_pcd = jest.fn()
    wrapper.vm.load_instance_list = jest.fn()
    wrapper.vm.calculate_main_canvas_dimension = jest.fn()
    wrapper.vm.calculate_secondary_canvas_dimension = jest.fn()
    wrapper.vm.load_instance_list = jest.fn()
    wrapper.vm.load_file_data = jest.fn()
    let spy = jest.spyOn(wrapper.vm, 'load_pcd')
    let spy2 = jest.spyOn(wrapper.vm, 'load_instance_list')
    let spy3 = jest.spyOn(wrapper.vm.$refs.x_axis_3d_canvas, 'destroy_canvas')
    let spy4 = jest.spyOn(wrapper.vm.$refs.y_axis_3d_canvas, 'destroy_canvas')
    let spy5 = jest.spyOn(wrapper.vm.$refs.z_axis_3d_canvas, 'destroy_canvas')
    let spy6 = jest.spyOn(wrapper.vm.$refs.main_3d_canvas, 'destroy_canvas')
    let spy7 = jest.spyOn(wrapper.vm, 'load_file_data')

    await wrapper.vm.reload_file_data()

    expect(spy).toHaveBeenCalled()
    expect(spy2).toHaveBeenCalled()
    expect(spy3).toHaveBeenCalled()
    expect(spy4).toHaveBeenCalled()
    expect(spy5).toHaveBeenCalled()
    expect(spy6).toHaveBeenCalled()
    expect(spy7).toHaveBeenCalled()
  });

  it("correctly calls reload_file_data()", async () => {
    options.propsData.file = {
      point_cloud: {
        url_signed: 'https://github.com/mrdoob/three.js/raw/master/examples/models/pcd/binary/Zaghetto.pcd'
      },
    }
    wrapper = shallowMount(sensor_fusion_editor, options);
    wrapper.setData({
      main_canvas_height: 100,
      main_canvas_width: 100,
      point_cloud_mesh: create_test_mesh(),
    })
    wrapper.vm.instance_update = jest.fn();

    wrapper.vm.$refs.main_3d_canvas = {
      destroy_canvas: jest.fn(),
      load_canvas: async () => {},
      scene_controller: {
        add_mesh_to_scene: jest.fn(),
        add_mesh_user_data_to_instance: jest.fn(),

      }
    };
    wrapper.vm.$refs.x_axis_3d_canvas = {
      destroy_canvas: jest.fn()
    };
    wrapper.vm.$refs.y_axis_3d_canvas = {
      destroy_canvas: jest.fn()
    };
    wrapper.vm.$refs.z_axis_3d_canvas = {
      destroy_canvas: jest.fn()
    };
    wrapper.vm.command_manager = {
      executeCommand: jest.fn(),
    }
    wrapper.vm.load_pcd = jest.fn()
    wrapper.vm.load_instance_list = jest.fn()
    wrapper.vm.calculate_main_canvas_dimension = jest.fn()
    wrapper.vm.calculate_secondary_canvas_dimension = jest.fn()
    wrapper.vm.load_instance_list = jest.fn()
    let spy1 = jest.spyOn(wrapper.vm.$refs.main_3d_canvas, 'load_canvas')
    let spy2 = jest.spyOn(wrapper.vm, 'calculate_main_canvas_dimension')
    let spy3 = jest.spyOn(wrapper.vm, 'calculate_secondary_canvas_dimension')
    let spy4 = jest.spyOn(wrapper.vm, 'load_instance_list')
    await wrapper.vm.load_file_data()

    expect(spy1).toHaveBeenCalled()
    expect(spy2).toHaveBeenCalled()
    expect(spy3).toHaveBeenCalled()
    expect(spy4).toHaveBeenCalled()

  });

  it("correctly calls set_save_loading()", async () => {
    options.propsData.file = {
      point_cloud: {
        url_signed: 'https://github.com/mrdoob/three.js/raw/master/examples/models/pcd/binary/Zaghetto.pcd'
      },
    }
    wrapper = shallowMount(sensor_fusion_editor, options);
    wrapper.setData({
      main_canvas_height: 100,
      main_canvas_width: 100,
      video_mode: true,
      point_cloud_mesh: create_test_mesh(),
      save_loading_frame: {},
    })
    wrapper.vm.set_save_loading('test1', 5)
    wrapper.vm.set_save_loading('test2', 8)

    expect(wrapper.vm.save_loading_frame['5']).toBe('test1')
    expect(wrapper.vm.save_loading_frame['8']).toBe('test2')


  });

  it("correctly calls get_save_loading()", async () => {
    options.propsData.file = {
      point_cloud: {
        url_signed: 'https://github.com/mrdoob/three.js/raw/master/examples/models/pcd/binary/Zaghetto.pcd'
      },
    }
    wrapper = shallowMount(sensor_fusion_editor, options);
    wrapper.setData({
      main_canvas_height: 100,
      main_canvas_width: 100,
      video_mode: true,
      point_cloud_mesh: create_test_mesh(),
      save_loading_frame: {
        5: 'test_get_save_loading'
      },
    })
    wrapper.vm.get_save_loading(5)

    expect(wrapper.vm.save_loading_frame['5']).toBe('test_get_save_loading')
    wrapper.setData({
      video_mode: false,
      save_loading_scene: 'test_2',
    })
    let result = wrapper.vm.get_save_loading()

    expect(result).toBe('test_2')

  });


});
