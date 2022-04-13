import Vuex from "vuex";
import Vuetify from "vuetify";
import {mount, createLocalVue, shallowMount} from "@vue/test-utils";
import label_schema_selector from "@/components/label/label_schema_selector";
import * as labelServices from '@/services/labelServices'
import * as eventServices from '@/components/event/create_event'
import {create_event} from "@/components/event/create_event";
import {get_schemas} from "@/services/labelServices";
const vuetify = new Vuetify();
const localVue = createLocalVue();

localVue.use(Vuex);

describe("Test label_schema_selector.vue", () => {
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

  it("Correctly calls on_change_schema()", async () => {
    const wrapper = mount(label_schema_selector, props, localVue);
    await wrapper.vm.on_change_schema()
    expect(wrapper.emitted().change).toBeTruthy()

  });


  it("Correctly calls on_filter_schemas()", async () => {
    const wrapper = mount(label_schema_selector, props, localVue);
    let val = 'test';
    let item = {name: 'test'};
    let search = 'tes'
    let res = wrapper.vm.on_filter_schemas(item, search, val)
    expect(res).toBeTruthy()

  });

  it("Correctly calls fetch_schema_list()", async () => {
    const wrapper = mount(label_schema_selector, props, localVue);
    let data = [{name: 'schema 1'}, {name: 'schema 2'}]
    labelServices.get_schemas = async () => {
      return [data, null]
    }
    await wrapper.vm.fetch_schema_list()
    expect(wrapper.vm.schema_list).toEqual(data)

  });




});
