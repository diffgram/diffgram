import text_annotation_core from "@/components/text_annotation/text_annotation_core.vue"
import { shallowMount, createLocalVue } from "@vue/test-utils";
import Vuex from "vuex";

const localVue = createLocalVue();
localVue.use(Vuex);

describe("text_annotation_core.vue", () => {
    it("Renders text interface loading state properly", () => {
        const wrapper = shallowMount(text_annotation_core, {}, localVue)
        expect(wrapper.text()).toEqual("Loading...")
    })
})

describe("Test draw_instance method of the text_annotation_core", () => {
    let wrapper;
    let props;

    beforeEach(() => {
        wrapper = shallowMount(text_annotation_core, {}, localVue)
    })

    it("draw_instances method has to return [] if no arguments supplied", () => {
        const rects = wrapper.vm.draw_instance()
        expect(rects).toEqual([])
    })

    it("draw_instances method has to return [] if any invalid argument supplied", () => {
        const draw_rects_with_string = wrapper.vm.draw_instance("string")
        expect(draw_rects_with_string).toEqual([])

        const draw_rects_with_number = wrapper.vm.draw_instance(1)
        expect(draw_rects_with_number).toEqual([])

        const draw_rects_with_array = wrapper.vm.draw_instance(["one"])
        expect(draw_rects_with_array).toEqual([])

        const draw_rects_with_empty_object = wrapper.vm.draw_instance({})
        expect(draw_rects_with_empty_object).toEqual([])
    })
})