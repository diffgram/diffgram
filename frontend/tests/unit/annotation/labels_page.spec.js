import Vuex from "vuex";
import Vuetify from "vuetify";
import {mount, createLocalVue} from "@vue/test-utils";
import labels_page from "@/components/annotation/labels_page";

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
          getters: {

          },
          mutations: {

          }
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
    wrapper.vm.api_update_schema = () => {return true}
    const spyUpdateSchema = jest.spyOn(wrapper.vm, 'api_update_schema')
    await wrapper.vm.archive_schema()
    expect(wrapper.vm.label_schema_list.map(elm => elm.id).includes(2)).toBeFalsy();
    expect(spyUpdateSchema).toHaveBeenCalled()
  });


});
