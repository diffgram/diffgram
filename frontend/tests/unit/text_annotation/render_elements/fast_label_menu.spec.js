import { shallowMount } from "@vue/test-utils";
import fast_label_menu from "../../../../src/components/text_annotation/render_elements/fast_label_menu.vue"

describe("Tests for fast_label_menu.vue", () => {
    const label_list = [
        {
            colour: {
                hex: "green"
            },
            label: {
                name: "Test label one"
            }
        },
        {
            colour: {
                hex: "red"
            },
            label: {
                name: "Test label two"
            }
        },
    ]

    it("Should be mounted succssfufully with rects prop", () => {
        const rects = [
            {
                x: 10,
                y:10,
                width: 20
            }
        ]

        const props = {
            propsData: {
                label_list,
                rects
            }
        }

        const wrapper = shallowMount(fast_label_menu, props)
        expect(wrapper.html()).toContain('style="top: 60px; left: 390px;"')
    })
})