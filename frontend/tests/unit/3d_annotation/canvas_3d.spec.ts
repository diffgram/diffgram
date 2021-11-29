import Vuex from "vuex";
import { shallowMount, createLocalVue } from "@vue/test-utils";
import canvas_3d from "../../../src/components/3d_annotation/canvas_3d.vue";
import * as THREE from "three";

const localVue = createLocalVue();
localVue.use(Vuex);

const create_test_mesh = function(){
  let geometry = new THREE.BoxGeometry( 2, 2, 2 );
  let material = new THREE.MeshBasicMaterial({
    color: new THREE.Color('red'),
    opacity: 1,
    transparent: true,
  });
  let mesh = new THREE.Mesh( geometry, material );
  return mesh
}

describe("Test canvas_3d.vue", () => {
  let options;

  beforeEach(() => {
    options = {
      propsData:{
        container_id: 'test_canvas_3d',
        point_cloud_mesh: create_test_mesh(),
      },
      mocks: {
        $get_sequence_color: () => {},
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
            get_view_issue_mode: () => {}
          }
        }
      }
    };
  });

  it("Tests if canvas_3d mounts successfully", () => {
    const wrapper = shallowMount(canvas_3d, options);
    expect(wrapper.html().includes(`id="${options.propsData.container_id}"`)).toBeTruthy();
  });
});
