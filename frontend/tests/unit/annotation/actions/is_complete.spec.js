import { shallowMount, createLocalVue } from "@vue/test-utils";
import is_complete from "@/components/annotation/actions/is_complete.vue";

describe("is_complete.vue", () => {
    let props;
    let testFunc;

    beforeEach(() => {
        testFunc = jest.fn()
        props = {
            propsData: {
                current_file: '',
                task_id: 1,
                task: {
                    id: 1,
                    status: ''
                }
            }
        }
    })

    it("Should render complete icon if task has status in_progress", () => {
        const wrapper = shallowMount(is_complete, props)
        expect(wrapper.html()).toContain('tooltip_message="Complete task"')
        expect(wrapper.html()).toContain('icon="mdi-check-circle-outline"')
    })

    it("Should render in review icon if task has status review_requested", () => {
        props.propsData.task.status = 'review_requested'
        const wrapper = shallowMount(is_complete, props)
        expect(wrapper.html()).toContain('tooltip_message="Complete task review"')
        expect(wrapper.html()).toContain('icon="mdi-archive-eye-outline"')
    })

    it("Should render completed regular_chip element if task has status complete", () => {
        props.propsData.task.status = 'complete'
        const wrapper = shallowMount(is_complete, props)
        expect(wrapper.findAll('regular_chip').length).toBe(1)
        expect(wrapper.html()).toContain("Complete")
    })

    it("Should trigger complete_dialog method when click on complete task icon", async () => {
        const wrapper = shallowMount(is_complete, props)
        wrapper.setMethods({ complete_dialog: testFunc })
        await wrapper.findAll('tooltip_button').trigger('click')
        expect(testFunc).toHaveBeenCalled()
    })
})