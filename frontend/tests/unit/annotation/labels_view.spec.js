import Vuex from "vuex";
import Vuetify from "vuetify";
import {mount, createLocalVue } from "@vue/test-utils";
import labels_view from "@/components/annotation/image_annotation/labels_view";
import * as labelServices from '@/services/labelServices'

const vuetify = new Vuetify();
const localVue = createLocalVue();
import axios from "../../../src/services/customInstance";

jest.mock('axios')
localVue.use(Vuex);

describe("Test labels_view.vue", () => {
  let props;

  beforeEach(() => {
    props = {
      mocks: {
        $get_sequence_color: () => {
        },
        task: 1,
        $store: {
          commit: function () {

          },
          watch: function () {

          },
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

  it("Correctly calls on_label_search()", async () => {
    const wrapper = mount(labels_view, props, localVue);
    let val = 'hello'
    let search = 'hello'
    let item = {
      label: {
        name: 'hello world'
      }
    }
    let result = wrapper.vm.on_label_search(val, search, item)
    expect(result).toBeTruthy();
  });


  it("Correctly calls generate_explore_url()", async () => {
    const wrapper = mount(labels_view, props, localVue);
    wrapper.vm.$store.state = {
      project: {
        current: {
          project_string_id: 'test'
        }
      }
    }
    let name = 'testing'
    let url = `/studio/annotate/${wrapper.vm.$store.state.project.current.project_string_id}/explorer?query=labels.${name} > 0`
    let result = wrapper.vm.generate_explore_url(name)
    expect(result).toEqual(url);
  });

  it("Correctly calls open_sample_labels_dialog()", async () => {
    const wrapper = mount(labels_view, props, localVue);
    wrapper.vm.$store.state = {
      project: {
        current: {
          project_string_id: 'test'
        }
      }
    }

    wrapper.vm.open_sample_labels_dialog()
    expect(wrapper.vm.dialog_confirm_sample_data).toEqual(true);
  });

  it("Correctly calls create_sample_labels()", async () => {
    const wrapper = mount(labels_view, props, localVue);
    wrapper.vm.$store.state = {
      project: {
        current: {
          project_string_id: 'test'
        }
      }
    }
    axios.post = async () => ({
      status: 200,
      data: {}
    })
    let spy = jest.spyOn(wrapper.vm, 'refresh_labels_function')
    await wrapper.vm.create_sample_labels()
    expect(wrapper.vm.dialog_confirm_sample_data).toEqual(false);
    expect(wrapper.vm.loading_create_sample_data).toEqual(false);
    expect(wrapper.vm.snackbar_success).toEqual(true);
    expect(spy).toHaveBeenCalled()
  });

  it("Correctly calls on_label_created()", async () => {
    const wrapper = mount(labels_view, props, localVue);
    await wrapper.vm.on_label_created()
    expect(wrapper.emitted().label_created).toBeTruthy()
  });

  it("Correctly calls expand_once()", async () => {
    const wrapper = mount(labels_view, props, localVue);
    wrapper.setData({
      video_mode: false,
      Labels: [{id: 1}]
    })
    wrapper.vm.$refs.label_data_table = {expanded: []}
    let spy = jest.spyOn(wrapper.vm, '$set')
    await wrapper.vm.expand_once()
    expect(wrapper.vm.expanded_once).toEqual(false)
    wrapper.setData({
      video_mode: true,
    })
    await wrapper.vm.expand_once()
    expect(wrapper.vm.expanded_once).toEqual(true)
    expect(spy).toHaveBeenCalledWith(wrapper.vm.$refs.label_data_table.expanded, wrapper.vm.Labels[0].id, true)
  });

  it("Correctly calls style_color()", async () => {
    const wrapper = mount(labels_view, props, localVue);
    let hex = '#e0e0e0'
    let result = wrapper.vm.style_color(hex)
    expect(result).toEqual(`color:${hex}`)
  });

  it("Correctly calls refresh_labels_function()", async () => {
    const wrapper = mount(labels_view, props, localVue);
    wrapper.setData({
      render_mode: 'full',
      project_string_id: 'test',
    })
    let res = {labels_out: [{id: 1, label: {name: 'a label'}}]}
    labelServices.get_labels = async () => {
      return [res, null]
    }
    let spy = jest.spyOn(labelServices, 'get_labels')
    let spy2 = jest.spyOn(wrapper.vm.$store, 'commit')
    await wrapper.vm.refresh_labels_function()
    expect(wrapper.vm.label_refresh_loading).toEqual(false)
    expect(spy).toHaveBeenCalled()
    expect(spy2).toHaveBeenCalledWith('finish_label_refresh')
    expect(wrapper.vm.Labels).toEqual(res.labels_out)
    expect(wrapper.emitted().label_file_colour_map).toBeTruthy()
    expect(wrapper.emitted().label_list).toBeTruthy()
    expect(wrapper.emitted().label_list).toBeTruthy()
    expect(wrapper.emitted().request_label_refresh_callback).toBeTruthy()
  });

  it("Correctly calls change_label_from_id_function()", async () => {
    const wrapper = mount(labels_view, props, localVue);
    wrapper.setData({
      Labels: [{id: 1}, {id: 2}, {id: 3}],
      project_string_id: 'test',
    })
    wrapper.vm.change_label_function = (id) => {
      return id
    }
    let spy = jest.spyOn(wrapper.vm, 'change_label_function')
    wrapper.vm.change_label_from_id_function(6)
    expect(spy).toHaveBeenCalledTimes(0)
    wrapper.vm.change_label_from_id_function(3)
    expect(spy).toHaveBeenCalledTimes(1)
    expect(spy).toHaveBeenCalledWith({id: 3})

  });


  it("Correctly calls change_label_function()", async () => {
    const wrapper = mount(labels_view, props, localVue);
    let testlabel = {id: 1, name: 'test'}
    wrapper.vm.change_label_function(testlabel)
    expect(wrapper.vm.current_label_file).toEqual(testlabel)
    expect(wrapper.emitted().change_label_file_function).toBeTruthy()

  });


  it("Correctly calls keyboard_events_window()", async () => {
    const wrapper = mount(labels_view, props, localVue);
    wrapper.setData({
      hotkey_dict: {
        25: {}
      },
      project_string_id: 'test',
    })
    wrapper.vm.$store.state = {
      user: {
        is_typing_or_menu_open: false
      }
    }
    let event = {keyCode: 25}
    let testlabel = {}
    wrapper.vm.keyboard_events_window(event)
    expect(wrapper.vm.current_label_file).toEqual({id: null})

  });

  it("Correctly calls api_file_update()", async () => {
    const wrapper = mount(labels_view, props, localVue);
    let data = {
      log: {
        info:{},
        mode: 'REMOVE'
      }
    }
    axios.post = async () => ({
      status: 200,
      data: data
    })
    let spy = jest.spyOn(wrapper.vm, 'refresh_labels_function')
    await wrapper.vm.api_file_update("REMOVE", {})
    expect(wrapper.vm.current_label_file).toEqual({id: null})
    expect(wrapper.vm.api_file_update_loading).toEqual(false)
    expect(wrapper.vm.info).toEqual(data.log.info)
    expect(wrapper.emitted().change_label_file_function).toBeTruthy()
    expect(spy).toHaveBeenCalled()
  });

  it("Correctly calls toggle_label_visible()", async () => {
    const wrapper = mount(labels_view, props, localVue);
    let label = {
      is_visible: "undefined"
    }
    wrapper.setData({
      Labels: [label]
    })
    await wrapper.vm.toggle_label_visible(label)
    expect(label.is_visible).toEqual(false)
    expect(wrapper.emitted().update_label_file_visible).toBeTruthy()
    expect(wrapper.vm.Labels.length === 1).toBeTruthy()

  });

});
