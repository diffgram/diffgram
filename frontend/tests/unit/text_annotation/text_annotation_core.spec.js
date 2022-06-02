import text_annotation_core from "@/components/text_annotation/text_annotation_core.vue"
import { shallowMount, createLocalVue } from "@vue/test-utils";
import Vuex from "vuex";

const localVue = createLocalVue();
localVue.use(Vuex);

describe("text_annotation_core.vue", () => {
    let props;

    beforeEach(() => {
        props = {
            propsData: {
                label_file_colour_map: {},
                label_list: [],
                project_string_id: "project_string_id",
                global_attribute_groups_list: [],
                per_instance_attribute_groups_list: [],
                label_schema: 1
            }
        }
    })

    it("Renders text interface loading state properly", () => {
        const wrapper = shallowMount(text_annotation_core, props, localVue)
        expect(wrapper.text()).toEqual("Loading...")
    })
})
