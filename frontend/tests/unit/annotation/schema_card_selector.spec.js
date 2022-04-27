import Vuex from "vuex";
import Vuetify from "vuetify";
import {mount, createLocalVue, shallowMount} from "@vue/test-utils";
import schema_card_selector from "@/components/annotation/schema_card_selector";
import * as labelServices from '@/services/labelServices'
import * as eventServices from '@/components/event/create_event'
import {create_event} from "@/components/event/create_event";

const vuetify = new Vuetify();
const localVue = createLocalVue();

localVue.use(Vuex);

describe("Test labels_page.vue", () => {
  let props;

  beforeEach(() => {
    props = {
      mocks: {
        $get_sequence_color: () => {
        },
        $route: {
          query: {}
        },
        task: 1,
        $store: {
          state: {
            project: {
              current_directory: {
                directory_id: -1
              },
              current: {
                project_string_id: "",

              }
            }
          },
          getters: {},
          mutations: {}
        },

      },
      vuetify
    };
  });

  it("Correctly calls select_schema()", async () => {
    const wrapper = mount(schema_card_selector, props, localVue);
    let schema = {name: 'test'};
    await wrapper.vm.select_schema(schema)
    expect(wrapper.vm.selected_schema).toEqual(schema)
    expect(wrapper.emitted().schema_selected).toBeTruthy()
  });

  it("Correctly calls create_schema()", async () => {
    let wrapper = mount(schema_card_selector, props, localVue);
    let schema = {name: 'test'};
    await wrapper.vm.create_schema(schema)
    expect(wrapper.vm.error.project).toBeDefined()
    wrapper.setProps({
      project_string_id: 'testt'
    })
    wrapper.setData({
      new_schema_name: undefined
    })
    await wrapper.vm.$nextTick()
    await wrapper.vm.create_schema(schema)
    expect(wrapper.vm.error.name).toBeDefined()
    wrapper.setData({
      new_schema_name: 'test'
    })
    wrapper.vm.$refs.menu = {
      close_menu: () => {
      }
    }
    wrapper.vm.$store.commit = () => {
    }
    let res = {
      dummy: 'test'
    }
    labelServices.create_schema = async () => {
      return [res, null]
    }
    const spy = jest.spyOn(labelServices, 'create_schema')
    const spy2 = jest.spyOn(wrapper.vm.$store, 'commit')
    const spy3 = jest.spyOn(wrapper.vm.$refs.menu, 'close_menu')
    await wrapper.vm.$nextTick()
    await wrapper.vm.create_schema(schema)
    expect(wrapper.vm.error.name).toBeUndefined()
    expect(wrapper.vm.error.project).toBeUndefined()
    expect(spy).toHaveBeenCalled()
    expect(spy2).toHaveBeenCalled()
    expect(spy3).toHaveBeenCalled()
    expect(wrapper.emitted().schema_created).toBeTruthy()
  });


});
