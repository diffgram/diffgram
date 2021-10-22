import context_menu_instance_template from "../../../src/components/context_menu/context_menu_instance_template";
import { shallowMount } from "@vue/test-utils";

describe("context_menu_instance_template.vue", () => {
  let instanceShape;
  let instance;

  beforeEach(() => {

  });


  it("Renders component correctly.", () => {
    const wrapper = shallowMount(context_menu_instance_template, {
      propsData:{

      }
    });
    expect(wrapper).toMatchSnapshot();
  });


});
