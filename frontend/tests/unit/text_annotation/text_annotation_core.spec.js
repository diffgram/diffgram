import text_annotation_core from "@/components/text_annotation/text_annotation_core.vue"
import { tokens, lines } from "./text_test_data"
import DrawRects from "../../../src/components/text_annotation/text_utils/draw_rects"
import InstanceList from "../../../src/helpers/instance_list"
import * as taskServices from "../../../src/services/tasksServices"
import { shallowMount, createLocalVue } from "@vue/test-utils";
import Vuex from "vuex";
import { TextAnnotationInstance } from "../../../embed/src/types/instances/TextInstance";

const localVue = createLocalVue();
localVue.use(Vuex);

describe("text_annotation_core.vue", () => {
    let props;
    let wrapper;
    let drawer;

    beforeEach(() => {
        props = {
            propsData: {
                label_file_colour_map: {},
                label_list: [],
                project_string_id: "project_string_id",
                global_attribute_groups_list: [],
                per_instance_attribute_groups_list: [],
                label_schema: 1,
            }
        }

        const instance_list = new InstanceList()
        drawer = new DrawRects(tokens, lines, instance_list)
        wrapper = shallowMount(text_annotation_core, props, localVue)

        wrapper.setData({
            tokens,
            lines,
            new_instance_list: instance_list,
            new_command_manager: {
                executeCommand: jest.fn()
            }
        })
    })

    it("Should properly update state when on_start_moving_borders is called", () => {
        wrapper.setData({
            show_label_selection: null,
            moving_border: null
        })

        wrapper.vm.on_start_moving_borders()

        expect(wrapper.vm.show_label_selection).toEqual(false)
        expect(wrapper.vm.moving_border).toEqual(true)
    })

    it("Should should set selection start border on on_change_selection_border", () => {
        wrapper.setData({
            selection_rects: drawer.generate_selection_rect(tokens[0].id, tokens[0].id),
            instance_in_progress: {}
        })

        const start_coordinate = {
            x: 50,
            y: 50
        }

        wrapper.vm.on_change_selection_border(start_coordinate, null)

        expect(wrapper.vm.instance_in_progress.start_token).toBeTruthy()
        expect(wrapper.vm.instance_in_progress.end_token).toEqual(tokens[0].id)
        expect(wrapper.vm.show_label_selection).toEqual(true)
        expect(wrapper.vm.moving_border).toEqual(false)
    })

    it("Should should set selection end border on on_change_selection_border", () => {
        wrapper.setData({
            selection_rects: drawer.generate_selection_rect(tokens[0].id, tokens[0].id),
            instance_in_progress: {}
        })

        const end_coordinate = {
            x: 50,
            y: 50
        }

        wrapper.vm.on_change_selection_border(null, end_coordinate)

        expect(wrapper.vm.instance_in_progress.end_token).toBeTruthy()
        expect(wrapper.vm.instance_in_progress.start_token).toEqual(tokens[0].id)
        expect(wrapper.vm.show_label_selection).toEqual(true)
        expect(wrapper.vm.moving_border).toEqual(false)
    })

    it("Should properly update state on on_open_context_menu", () => {
        const preventDefault = jest.fn()

        const e = {
            preventDefault
        }

        wrapper.vm.on_open_context_menu(e, {})

        expect(preventDefault).toHaveBeenCalled()
        expect(wrapper.vm.current_instance).toBeTruthy()
    })

    it("Should emit change_label_schema on on_change_label_schema", () => {
        wrapper.vm.on_change_label_schema(2)
        expect(wrapper.emitted('change_label_schema')).toBeTruthy()
    })

    it("Should successully save task and call next task trigger of the status is not complete on on_task_annotation_complete_and_save", async () => {
        const task = {
            id: 1
        }

        const response = {
            data: {
                task: {
                    status: "complete"
                }
            }
        }

        props.propsData.task = task;
        const local_wrapper = shallowMount(text_annotation_core, props, localVue)

        const mock = jest.spyOn(taskServices, 'finishTaskAnnotation')
        mock.mockReturnValue(response);

        local_wrapper.vm.save = jest.fn();
        local_wrapper.vm.trigger_task_change = jest.fn();

        await local_wrapper.vm.on_task_annotation_complete_and_save()

        expect(local_wrapper.vm.save).toHaveBeenCalled()
        expect(local_wrapper.vm.trigger_task_change).toHaveBeenCalled()
        mock.mockRestore();
    })

    it("Should not create instances on the bulk label if the instance contain more than one token", () => {
        const bulk_test_instance = new TextAnnotationInstance()
        bulk_test_instance.create_instance(1, 1, 2, {})
        wrapper.vm.new_instance_list.push([bulk_test_instance])

        const initial_instance_snapshot = wrapper.vm.new_instance_list.get_all()

        wrapper.vm.bulk_labeling(1)

        const final_instance_snapshot = wrapper.vm.new_instance_list.get_all()

        expect(initial_instance_snapshot).toEqual(final_instance_snapshot)
    })

    it("Should perform bulk label on all the avalible tokens", async () => {
        const test_token = tokens.find(token => {
            const word = token.word
            const token_count = tokens.filter(tok => tok.word === word).length
            if (token_count > 1) return token
        })
        const test_token_count = tokens.filter(token => token.word === test_token.word).length

        const bulk_test_instance = new TextAnnotationInstance()
        bulk_test_instance.create_instance(1, test_token.id, test_token.id, {})
        wrapper.vm.new_instance_list.push([bulk_test_instance])

        await wrapper.vm.bulk_labeling(1)
        const number_of_instances = wrapper.vm.new_instance_list.get_all().length


        expect(number_of_instances).toEqual(test_token_count)
    })

    it("Should trigger bulk label if the control is not pressed while clicking and if bulk label is set to true", () => {
        wrapper.setData({
            bulk_label: true
        })

        wrapper.vm.bulk_labeling = jest.fn()

        wrapper.vm.on_trigger_instance_click({}, 1)

        expect(wrapper.vm.bulk_labeling).toHaveBeenCalled()
    })

    it("Should trigger create relation if the control is not pressed while clicking and if bulk label is not set to true", () => {
        wrapper.vm.on_draw_relation = jest.fn()

        wrapper.vm.on_trigger_instance_click({}, 1)

        expect(wrapper.vm.on_draw_relation).toHaveBeenCalled()
    })

    it("Should not fire bulk_labeling or on_draw_relation if control + click event", () => {
        const event = {
            ctrlKey: true,
            button: 0
        }

        wrapper.vm.bulk_labeling = jest.fn()
        wrapper.vm.on_draw_relation = jest.fn()

        wrapper.vm.on_trigger_instance_click(event, 1)

        expect(wrapper.vm.bulk_labeling).not.toHaveBeenCalled()
        expect(wrapper.vm.on_draw_relation).not.toHaveBeenCalled()
    })
})
