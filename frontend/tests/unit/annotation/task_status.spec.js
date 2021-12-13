import Vuex from "vuex";
import { shallowMount, createLocalVue } from "@vue/test-utils";
import task_status from "@/components/annotation/task_status.vue";

const localVue = createLocalVue();
localVue.use(Vuex);

describe("task_status.vue", () => {
    let props;

    beforeEach(() => {
        props = {
            propsData: {
                task_status: "complete"
            },
        };
    });
    
    it("Renders Completed message when the status is complete", () => {
        const wrapper = shallowMount(task_status, props, localVue);
        expect(wrapper.html()).toContain('tooltip_message="Completed" color="green"')
    });

    it("Renders Requires changes message when the status is requires_changes", () => {
        props.propsData.task_status = "requires_changes"
        const wrapper = shallowMount(task_status, props, localVue);
        expect(wrapper.html()).toContain('tooltip_message="Requires changes" color="red"')
    });

    it("Renders In review message when the status is review_requested", () => {
        props.propsData.task_status = "review_requested"
        const wrapper = shallowMount(task_status, props, localVue);
        expect(wrapper.html()).toContain('tooltip_message="In review"')
    });

    it("Renders In progress message when the status is in_progress", () => {
        props.propsData.task_status = "in_progress"
        const wrapper = shallowMount(task_status, props, localVue);
        expect(wrapper.html()).toContain('tooltip_message="In progress"')
    });
});
