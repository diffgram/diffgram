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
