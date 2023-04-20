import text_sidebar from "../../../src/components/annotation/text_annotation/text_sidebar.vue"
import { shallowMount, createLocalVue } from "@vue/test-utils";
import { instance_list } from "./text_test_data"
import { TextAnnotationInstance } from "../../../src/components/vue_canvas/instances/TextInstance";
import {
    BaseAnnotationUIContext,
    TextAnnotationUIContext
  } from "../../../src/types/AnnotationUIContext"
import InstanceStore from "../../../src/helpers/InstanceStore";
import CommandManager from "../../../src/helpers/command/command_manager"
import History from "../../../src/helpers/history"
import Vuex from "vuex";

const localVue = createLocalVue();
localVue.use(Vuex);

describe("text_sidebar.vue", () => {
    let props;
    let wrapper;
    let test_instance;

    beforeEach(() => {
        const annotation_ui_context = new BaseAnnotationUIContext()
        annotation_ui_context.working_file = {
            id: 1,
            type: "text"
        }
        annotation_ui_context.instance_store = new InstanceStore()
        annotation_ui_context.label_schema = {
            id: 69,
            name: "POS tags",
            project_id: 20,
        }
        annotation_ui_context.history = new History()
        annotation_ui_context.command_manager = new CommandManager(annotation_ui_context.history)
        
        const child_annotation_ctx_list = [new TextAnnotationUIContext()]
        annotation_ui_context.current_text_annotation_ctx = child_annotation_ctx_list[0]

        test_instance = new TextAnnotationInstance()

        props = {
            propsData: {
                project_string_id: "project_string",
                schema_id: 1,
                instance_list: instance_list.get_all(),
                loading: false,
                per_instance_attribute_groups_list: [],
                label_list: [],
                annotation_ui_context: annotation_ui_context,
                image_annotation_ctx: child_annotation_ctx_list[0],
                child_annotation_ctx_list: child_annotation_ctx_list,
                instance_store: annotation_ui_context.instance_store,
                working_file: annotation_ui_context.working_file
            },
            mocks: {
                $store: {
                    state: {
                        user: {
                            current: {
                                is_super_admin: true
                            }
                        }
                    }
                }
            }
        }

        wrapper = shallowMount(text_sidebar, props, localVue)
    })

    it("Should not return id column if the user is not a super_admin", () => {
        props.mocks.$store.state.user.current.is_super_admin = false

        const local_wrapper = shallowMount(text_sidebar, props, localVue)
        const id_header = local_wrapper.vm.headers.find(header => header.value === 'id')
        expect(id_header).not.toBeTruthy()
    })

    it("Should have basic expansion panes", () => {
        const text = wrapper.text()
        expect(text).toContain('Attributes')
        expect(text).toContain('Instances')
    })

    it("Should successfully change state of open panels", () => {
        wrapper.setData({
            open_panels: [1]
        })

        wrapper.vm.on_change_expansion(0)
        expect(wrapper.vm.open_panels).toContain(0)
        wrapper.vm.on_change_expansion(0)
        expect(wrapper.vm.open_panels).not.toContain(0)
    })

    it("Should emit on_instance_hover event on on_hover_item", () => {
        wrapper.vm.on_hover_item(test_instance)
        expect(wrapper.emitted('on_instance_hover')).toBeTruthy()
    })

    it("Should emit on_instance_stop_hover on on_stop_hover_item", () => {
        wrapper.vm.on_stop_hover_item()
        expect(wrapper.emitted('on_instance_stop_hover')).toBeTruthy()
    })

    it("Should emit on_select_instance event on on_select_instance", () => {
        wrapper.vm.on_select_instance(test_instance)
        expect(wrapper.emitted('on_select_instance')).toBeTruthy()
    })

    it("Should return empty array if one of the properties is not set", () => {
        let local_wrapper;
        let result;

        props.propsData.label_list = undefined
        props.propsData.current_instance = undefined
        props.propsData.per_instance_attribute_groups_list = undefined

        local_wrapper = shallowMount(text_sidebar, props, localVue)
        result = local_wrapper.vm.attribute_group_list_prop()
        expect(result).toEqual([])

        props.propsData.label_list = [1]
        local_wrapper = shallowMount(text_sidebar, props, localVue)
        result = local_wrapper.vm.attribute_group_list_prop()
        expect(result).toEqual([])

        props.propsData.current_instance = {id: 1}
        local_wrapper = shallowMount(text_sidebar, props, localVue)
        result = local_wrapper.vm.attribute_group_list_prop()
        expect(result).toEqual([])

        props.propsData.per_instance_attribute_groups_list = [{id: 1}]
        local_wrapper = shallowMount(text_sidebar, props, localVue)
        result = local_wrapper.vm.attribute_group_list_prop()
        expect(result).toEqual([])
    })

    it("Should return array of attributes", () => {
        props.propsData.label_list = [{id : 1}]
        props.propsData.current_instance = {
            id: 1,
            label_file: {
                id: 1
            }
        }
        props.propsData.per_instance_attribute_groups_list = [
            {
                label_file_list: [
                    {
                        id: 1
                    }
                ]
            }
        ]

        const local_wrapper = shallowMount(text_sidebar, props, localVue)
        const result = local_wrapper.vm.attribute_group_list_prop()
        expect(result).toEqual(props.propsData.per_instance_attribute_groups_list)
    })

    it("Should emit on_update_attribute on attribute_change", () => {
        wrapper.vm.attribute_change({})
        expect(wrapper.emitted('on_update_attribute')).toBeTruthy()
    })
})
