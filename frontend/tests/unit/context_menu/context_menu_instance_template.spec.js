import context_menu_instance_template from "../../../src/components/context_menu/context_menu_instance_template";
import {shallowMount, createLocalVue} from "@vue/test-utils";
import Vuex from 'vuex'

const localVue = createLocalVue();
localVue.use(Vuex)

describe("context_menu_instance_template.vue", () => {
  let actions;
  let store;

  beforeEach(() => {
    actions = {
      actionClick: jest.fn(),
      actionInput: jest.fn()
    }
    store = new Vuex.Store({
      actions
    })
  });


  it("Renders component correctly.", () => {
    const wrapper = shallowMount(context_menu_instance_template, {
      store,
      localVue,
      propsData: {}
    });
    expect(wrapper).toMatchSnapshot();
  });

  it("Sets data prop of open menu when calling on_click_set_node_name().", () => {
    const wrapper = shallowMount(context_menu_instance_template, {
      store,
      localVue,
      propsData: {}
    });
    const spyCommit = jest.spyOn(wrapper.vm.$store, 'commit')
    wrapper.vm.on_click_set_node_name()
    expect(wrapper.vm.show_set_node_name_menu).toBe(true);
    expect(spyCommit).toHaveBeenCalledWith('set_user_is_typing_or_menu_open', true)
  });


  it("Sets data prop of open menu when calling on_close_node_name_menu().", () => {
    const wrapper = shallowMount(context_menu_instance_template, {
      store,
      localVue,
      propsData: {}
    });
    const spyCommit = jest.spyOn(wrapper.vm.$store, 'commit')
    wrapper.vm.on_close_node_name_menu()
    expect(wrapper.vm.show_set_node_name_menu).toBe(false);
    expect(spyCommit).toHaveBeenCalledWith('set_user_is_typing_or_menu_open', false)
  });

  it("Emits events when calling emit_update_and_hide_menu().", () => {
    const wrapper = shallowMount(context_menu_instance_template, {
      store,
      localVue,
      propsData: {}
    });
    wrapper.vm.emit_update_and_hide_menu()
    expect(wrapper.emitted().instance_update.length).toBe(1);
    expect(wrapper.emitted().hide_context_menu.length).toBe(1);
  });

  it("Occludes instance when calling on_click_occluded().", () => {
    const wrapper = shallowMount(context_menu_instance_template, {
      store,
      localVue,
      propsData: {
        instance: {
          toggle_occluded: () => {
          }
        }
      }
    });
    wrapper.vm.node_hover_index_locked = 5;
    const spyToggle = jest.spyOn(wrapper.vm.instance, 'toggle_occluded')
    wrapper.vm.on_click_occluded()
    expect(spyToggle).toHaveBeenCalledWith(5)
    expect(wrapper.emitted().hide_context_menu.length).toBe(1);
  });


  it("It closes and emits update when calling on_node_updated().", () => {
    const wrapper = shallowMount(context_menu_instance_template, {
      store,
      localVue,
      propsData: {
        instance: {
          toggle_occluded: () => {
          }
        }
      }
    });
    wrapper.vm.node_hover_index_locked = 5;
    const spyTest = jest.spyOn(wrapper.vm, 'emit_update_and_hide_menu')
    wrapper.vm.on_node_updated()
    expect(spyTest).toHaveBeenCalledWith({
      index: wrapper.vm.instance_hover_index_locked,
      node_hover_index: wrapper.vm.node_hover_index_locked,
      mode: 'node_name_changed',
    })
    expect(wrapper.emitted().hide_context_menu.length).toBe(1);
  });

  it("It emit close event when calling close().", () => {
    const wrapper = shallowMount(context_menu_instance_template, {
      store,
      localVue,
      propsData: {
        instance: {
          toggle_occluded: () => {
          }
        }
      }
    });
    const spyTest = jest.spyOn(wrapper.vm.$store, 'commit')
    wrapper.vm.close()
    expect(spyTest).toHaveBeenCalledWith('set_user_is_typing_or_menu_open', false)
    expect(wrapper.vm.show_set_node_name_menu).toBe(false);
  });

  it("Correctly sets values when calling get_mouse_position().", () => {
    let mouse_position_mock = {
      x: 1,
      y: 2,
      raw: {
        x: 3,
        y: 4
      }
    }
    const wrapper = shallowMount(context_menu_instance_template, {
      store,
      localVue,
      propsData: {
        mouse_position: mouse_position_mock
      }
    });
    const spyTest = jest.spyOn(wrapper.vm.$store, 'commit')
    wrapper.vm.get_mouse_position();
    expect(wrapper.vm.top).toBe(wrapper.vm.mouse_position.raw.y + 'px');
    expect(wrapper.vm.left).toBe(wrapper.vm.mouse_position.raw.x + 'px');
    expect(wrapper.vm.locked_mouse_position).toMatchObject(mouse_position_mock);
  });

  it("Correctly updates mouse position when calling show_context_menu().", async () => {
    const wrapper = shallowMount(context_menu_instance_template, {
      store,
      localVue,
      propsData: {
        instance: {
          node_hover_index: 5
        },
        mouse_position: {
          x: 1,
          y: 2,
          raw: {
            x: 3,
            y: 4
          }
        }
      }
    });
    const spyTest = jest.spyOn(wrapper.vm.$options.watch, 'show_context_menu')
    const spyMouse = jest.spyOn(wrapper.vm, 'get_mouse_position')
    wrapper.setProps({ show_context_menu: true});
    wrapper.setData({instance_hover_index: 7 })
    await wrapper.vm.$nextTick();
    expect(spyMouse).toHaveBeenCalled()
    expect(wrapper.vm.instance_hover_index_locked).toBe(wrapper.vm.instance_hover_index);
    expect(wrapper.vm.node_hover_index_locked).toBe(wrapper.vm.instance.node_hover_index);

  });

});
