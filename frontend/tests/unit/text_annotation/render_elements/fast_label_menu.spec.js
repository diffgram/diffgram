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

    const rects = [
        {
            x: 10,
            y:10,
            width: 20
        }
    ]

    const arrow_position = {
        x: 10,
        y: 10
    }

    it("Should be mounted succssfufully with rects prop", () => {
        const props = {
            propsData: {
                label_list,
                rects
            }
        }

        const wrapper = shallowMount(fast_label_menu, props)
        expect(wrapper.html()).toContain('style="top: 60px; left: 390px;"')
    })

    it("Should be mounted succssfufully with arrow_position prop", () => {
        const props = {
            propsData: {
                label_list,
                arrow_position
            }
        }

        const wrapper = shallowMount(fast_label_menu, props)
        expect(wrapper.html()).toContain('style="top: 35px; left: 360px;"')
    })

    it("on_apply_label should emit create_instance event if rects props is provided", () => {
        const props = {
            propsData: {
                label_list,
                rects
            }
        }

        const wrapper = shallowMount(fast_label_menu, props)
        wrapper.vm.on_apply_label(label_list[0])

        expect(wrapper.emitted('create_instance')).toBeTruthy()
    })

    it("on_apply_label should emit create_instance event if rects arrow_position is provided", () => {
        const props = {
            propsData: {
                label_list,
                arrow_position
            }
        }

        const wrapper = shallowMount(fast_label_menu, props)
        wrapper.vm.on_apply_label(label_list[0])

        expect(wrapper.emitted('create_relation')).toBeTruthy()
    })
})