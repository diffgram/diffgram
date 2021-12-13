import Vuex from "vuex";
import {shallowMount, createLocalVue, Wrapper} from "@vue/test-utils";
import hotkeys_sensor_fusion from "../../../src/components/3d_annotation/hotkeys_sensor_fusion";

jest.mock("three/src/renderers/WebGLRenderer"); // this happens automatically with automocking
const localVue = createLocalVue();
localVue.use(Vuex);


window.alert = jest.fn();
let options, wrapper, actions, store;
describe("Test context_menu_3d_editor.vue", () => {


  beforeEach(() => {
    actions = {
      actionClick: jest.fn(),
      actionInput: jest.fn()
    }
    store = new Vuex.Store({
      actions,
      mutations:{
        'set_user_is_typing_or_menu_open': jest.fn(),
      }
    })
    options = {
      localVue: localVue,
      store: store,
      propsData: {},
      mocks: {}
    };
  });

  it("Tests if context_menu_3d_editor mounts successfully", () => {
    wrapper = shallowMount(hotkeys_sensor_fusion, options);
    expect(wrapper.html().includes(`id="hotkeys-3d"`)).toBeTruthy();
  });

});
