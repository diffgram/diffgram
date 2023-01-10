import Vuex from "vuex";
import Vuetify from "vuetify";
import {mount, createLocalVue, shallowMount} from "@vue/test-utils";
import labels_page from "@/components/annotation/image_annotation/labels_page";
import * as labelServices from '@/services/labelServices'
import * as eventServices from '@/components/event/create_event'
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

  it("Correctly calls archive_schema()", async () => {
    const wrapper = mount(labels_page, props, localVue);
    wrapper.setData({
      label_schema_list: [
        {name: 'test', id: 1},
        {name: 'test2', id: 2},
        {name: 'test3', id: 3},
      ],
      current_schema: {
        name: 'test2', id: 2
      }
    })
    wrapper.vm.api_update_schema = () => {
      return true
    }
    const spyUpdateSchema = jest.spyOn(wrapper.vm, 'api_update_schema')
    await wrapper.vm.archive_schema()
    expect(wrapper.vm.label_schema_list.map(elm => elm.id).includes(2)).toBeFalsy();
    expect(spyUpdateSchema).toHaveBeenCalled()
  });

  it("Correctly calls update_schema_name()", async () => {
    const wrapper = shallowMount(labels_page, props, localVue);
    wrapper.setData({
      label_schema_list: [
        {name: 'test', id: 1},
        {name: 'test2', id: 2},
        {name: 'test3', id: 3},
      ],
      current_schema: {
        name: 'test2', id: 2
      }
    })
    wrapper.vm.api_update_schema = async () => {
      return true
    }
    const spyUpdateSchema = jest.spyOn(wrapper.vm, 'api_update_schema')
    await wrapper.vm.update_schema_name({
      name: 'test2', id: 2
    })
    expect(spyUpdateSchema).toHaveBeenCalled()
  });

  it("Correctly calls api_update_schema()", async () => {
    const wrapper = shallowMount(labels_page, props, localVue);
    wrapper.setData({
      label_schema_list: [
        {name: 'test', id: 1},
        {name: 'test2', id: 2},
        {name: 'test3', id: 3},
      ],
      current_schema: {
        name: 'test2', id: 2
      }
    })
    labelServices.update_schema = async () => {
      return [{name:'test'}, null]
    }
    const spyUpdateSchema = jest.spyOn(labelServices, 'update_schema')
    await wrapper.vm.api_update_schema({
      name: 'test2', id: 2
    })
    expect(spyUpdateSchema).toHaveBeenCalled()
  });

  it("Correctly calls on_schema_created()", async () => {
    const wrapper = mount(labels_page, props, localVue);
    wrapper.setData({
      label_schema_list: [
        {name: 'test', id: 1},
        {name: 'test2', id: 2},
        {name: 'test3', id: 3},
      ],
      current_schema: {
        name: 'test2', id: 2
      }
    })
    const spy = jest.spyOn(wrapper.vm.$refs.schema_selector, 'select_schema')
    await wrapper.vm.on_schema_created({
      name: 'test2', id: 56
    })
    expect(wrapper.vm.label_schema_list.map(elm => elm.id).includes(56)).toBeTruthy()
    expect(spy).toHaveBeenCalled()
  });


  it("Correctly calls on_schema_selected()", async () => {
    const wrapper = mount(labels_page, props, localVue);
    wrapper.setData({
      label_schema_list: [
        {name: 'test', id: 1},
        {name: 'test2', id: 2},
        {name: 'test3', id: 3},
      ],
      current_schema: {
        name: 'test2', id: 2
      }
    })
    let data = {
      name: 'test2', id: 56
    }
    await wrapper.vm.on_schema_selected(data)
    expect(wrapper.vm.current_schema).toEqual(data)
  });

  it("Correctly calls fetch_schemas()", async () => {
    const wrapper = mount(labels_page, props, localVue);
    wrapper.setData({
      label_schema_list: [
        {name: 'test', id: 1},
        {name: 'test2', id: 2},
        {name: 'test3', id: 3},
      ],
      current_schema: {
        name: 'test2', id: 2
      }
    })
    let data = {
      name: 'test2', id: 56
    }
    let testresult = [{name:'test'}]
    labelServices.get_schemas = async () => {
      return [testresult, null]
    }
    const spy = jest.spyOn(wrapper.vm.$refs.schema_selector, 'select_schema')
    await wrapper.vm.fetch_schemas(data)
    expect(wrapper.vm.label_schema_list).toEqual(testresult)
    expect(spy).toHaveBeenCalled()
  });

  it("Correctly calls add_visit_history_event()", async () => {
    const wrapper = mount(labels_page, props, localVue);
    wrapper.setData({
      label_schema_list: [
        {name: 'test', id: 1},
        {name: 'test2', id: 2},
        {name: 'test3', id: 3},
      ],
      current_schema: {
        name: 'test2', id: 2
      }
    })
    let data = {
      name: 'test2', id: 56
    }

    eventServices.create_event = async () => {
      return {name: 'test', type: 'test'}
    }
    const spy = jest.spyOn(eventServices, 'create_event')
    await wrapper.vm.add_visit_history_event(data)
    expect(spy).toHaveBeenCalled()
  });


});
