import Vuex from "vuex";
import {shallowMount, createLocalVue, Wrapper} from "@vue/test-utils";
import context_menu_3d_editor from "../../../src/components/3d_annotation/context_menu_3d_editor.vue";
import Vue from "vue";

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
    wrapper = shallowMount(context_menu_3d_editor, options);
    expect(wrapper.html().includes(`class="context-menu"`)).toBeTruthy();
  });

  it("correctly calls show_instance_history_panel()", () => {
    wrapper = shallowMount(context_menu_3d_editor, options);
    wrapper.vm.show_instance_history_panel()
    expect(wrapper.emitted().open_instance_history_panel.length).toBe(1);

  });

  it("correctly calls close()", () => {
    wrapper = shallowMount(context_menu_3d_editor, {
        store,
        localVue,
        propsData: {}
      }
    );
    const spyCommit = jest.spyOn(wrapper.vm.$store, 'commit')
    wrapper.vm.close()
    expect(wrapper.emitted().close_context_menu.length).toBe(1);
    expect(spyCommit).toHaveBeenCalledWith('set_user_is_typing_or_menu_open', false)

  });

  it("correctly calls get_mouse_position()", () => {
    let mouse_position = {
      screen_y: 85,
      screen_x: 74,
    };
    wrapper = shallowMount(context_menu_3d_editor, {
        store,
        localVue,
        propsData: {
          mouse_position
        }
      }
    );
    wrapper.vm.get_mouse_position();
    expect(wrapper.vm.top).toBe(mouse_position.screen_y + 'px');
    expect(wrapper.vm.left).toBe(mouse_position.screen_x + 'px');
    expect(wrapper.vm.locked_mouse_position).toMatchObject(mouse_position);

  });

  it("correctly calls on_click_delete_instance()", () => {
    wrapper = shallowMount(context_menu_3d_editor, options);
    wrapper.vm.on_click_delete_instance()
    expect(wrapper.emitted().delete_instance.length).toBe(1);

  });

  it("correctly calls show_share_context_menu()", () => {
    wrapper = shallowMount(context_menu_3d_editor, {
        store,
        localVue,
        propsData: {}
      }
    );
    const spyCommit = jest.spyOn(wrapper.vm.$store, 'commit');
    wrapper.vm.show_share_context_menu();
    expect(wrapper.vm.show_share_instance_menu).toBe(true);
    expect(spyCommit).toHaveBeenCalledWith('set_user_is_typing_or_menu_open', true)
    expect(wrapper.emitted().share_dialog_open.length).toBe(1);

  });

  it("correctly calls on_click_copy_instance()", () => {
    wrapper = shallowMount(context_menu_3d_editor, {
        store,
        localVue,
        propsData: {}
      }
    );
    const spyCommit = jest.spyOn(wrapper.vm, 'close');
    wrapper.vm.on_click_copy_instance();
    expect(wrapper.emitted().copy_instance.length).toBe(1);
    expect(spyCommit).toHaveBeenCalledWith()
  });

  it("correctly calls open_issue_panel()", () => {
    wrapper = shallowMount(context_menu_3d_editor, {
        store,
        localVue,
        propsData: {}
      }
    );
    wrapper.vm.open_issue_panel();
    expect(wrapper.emitted().open_issue_panel.length).toBe(1);
  });

  it("correctly calls on_click_paste_instance()", () => {
    wrapper = shallowMount(context_menu_3d_editor, {
        store,
        localVue,
        propsData: {}
      }
    );
    const spyClose = jest.spyOn(wrapper.vm, 'close');
    wrapper.vm.on_click_paste_instance();
    expect(wrapper.emitted().paste_instance.length).toBe(1);
    expect(spyClose).toHaveBeenCalledWith()
  });

  it("correctly calls close_share_dialog()", () => {
    wrapper = shallowMount(context_menu_3d_editor, {
        store,
        localVue,
        propsData: {}
      }
    );
    const spyClose = jest.spyOn(wrapper.vm.$store, 'commit');
    wrapper.vm.close_share_dialog();
    expect(wrapper.emitted().share_dialog_close.length).toBe(1);
    expect(spyClose).toHaveBeenCalledWith('set_user_is_typing_or_menu_open', false)
  });

});
