import { shallowMount } from "@vue/test-utils";
import relation_in_progress from "../../../../src/components/text_annotation/render_elements/relation_in_progress.vue"

describe("Tests for relation_in_progress.vue", () => {
    let wrapper;
    let props;

    beforeEach(() => {
        props = {
            propsData: {
                render_drawing_arrow: {
                    marker: {
                        x: 1,
                        y: 1
                    },
                    path: 'M 1 1 Q 10 10 5 5',
                    arrow: {
                        x: 10,
                        y: 10
                    }
                }
            }
        }

        wrapper = shallowMount(relation_in_progress, props)
    })

    it("Should render corectly circle element", () => {
        expect(wrapper.html()).toContain('<circle cx="1" cy="1" fill="rgba(76, 139, 245)" r="3" class="unselectable"></circle>')
    })

    it("Should render corectly arrow element", () => {
        expect(wrapper.html()).toContain('<path d="M 10 10 l -5, -5 l 10, 0 l -5, 5" fill="rgba(76, 139, 245)" class="unselectable"></path>')
    })

    it("Should render corectly path element", () => {
        expect(wrapper.html()).toContain('<path stroke="rgba(76, 139, 245)" d="M 1 1 Q 10 10 5 5" fill="transparent" class="unselectable"></path>')
    })
})
