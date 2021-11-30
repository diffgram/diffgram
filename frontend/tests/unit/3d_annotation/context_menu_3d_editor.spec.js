import Vuex from "vuex";
import {shallowMount, createLocalVue, Wrapper} from "@vue/test-utils";
import context_menu_3d_editor from "../../../src/components/3d_annotation/context_menu_3d_editor.vue";
import Vue from "vue";
jest.mock("three/src/renderers/WebGLRenderer"); // this happens automatically with automocking
const localVue = createLocalVue();
localVue.use(Vuex);


window.alert = jest.fn();

describe("Test context_menu_3d_editor.vue", () => {
  let options, wrapper;
  beforeEach(() => {
    options = {
      propsData: {

      },
      mocks: {

      }
    };
  });

  it("Tests if context_menu_3d_editor mounts successfully", () => {
    wrapper = shallowMount(context_menu_3d_editor, options);
    expect(wrapper.html().includes(`class="context-menu"`)).toBeTruthy();
  });



});
