import text_context_menu from "../../../../src/components/annotation/text_annotation/render_elements/text_context_menu.vue"
import { shallowMount } from "@vue/test-utils";

describe("Tests text_context_menu.vue", () => {
    let props;
    let wrapper;

    beforeEach(() => {
        props = {
            propsData: {
                context_menu: {
                    x: 1,
                    y: 1,
                    instance: {
                        label_file: {
                            colour: {
                                hex: "#fff"
                            },
                            label: {
                                name: "Test label"
                            }
                        }
                    }
                }
            }
        }

        wrapper = shallowMount(text_context_menu, props)
    })

    it("Should render context menu on the provided position", () => {
        expect(wrapper.html()).toContain('class="fast-menu-element" style="top: 1px; left: 1px;"')
    })

    it("Should render correct label color", () => {
        expect(wrapper.html()).toContain('<strong style="color: rgb(255, 255, 255);">')
    })

    it("Should render correct label name", () => {
        expect(wrapper.text()).toContain('Test label')
    })

    it("Should not dispay any attributes when instance doesn't have any", () => {
        expect(wrapper.text()).not.toContain('Attributes:')
    })

    it("Should dispay attributes when instance has attributes", () => {
        props.propsData.context_menu.instance.attribute_groups = {
            "key_one": {
                display_name: "Attribute one"
            },
            "kay_two": {
                display_name: "Attribute two"
            }
        }
        wrapper = shallowMount(text_context_menu, props)

        expect(wrapper.text()).toContain('Attributes: Attribute one, Attribute two')
    })

    it("Should trigger delete fucntion when delete is pressed", async () => {
        wrapper.vm.on_delete()
        expect(wrapper.emitted('delete_instance')).toBeTruthy()
    })
})