import text_context_menu from "../../../../src/components/text_annotation/render_elements/text_context_menu.vue"
import { shallowMount } from "@vue/test-utils";

describe("Tests text_context_menu.vue", () => {
    let props;

    beforeEach(() => {
        props = {
            propsData: {
                context_menu: {
                    x: 2,
                    y: 2,
                    instance: {
                        label_file: {
                            colour: {},
                            label: {}
                        }
                    }
                }
            }
        }
    })

    it("yo", () => {
        const wrapper = shallowMount(text_context_menu, props)
    })
})