import selection from "../../../../src/components/annotation/text_annotation/render_elements/selection.vue"
import { shallowMount } from "@vue/test-utils";

describe("Tests for selection.vue", () => {   
    let wrapper;

    const rects = [
        {
            x: 10,
            y:10,
            width: 20
        }
    ]

    const props = {
        propsData: {
            rects
        }
    }

    beforeEach(() => {
        wrapper = shallowMount(selection, props)
    })

    it("Should properly render selection svg component", () => {
        const html = wrapper.html()
        expect(html).toContain('circle cx="8" cy="10" r="4"')
        expect(html).toContain('rect x="8" y="10" width="1" height="25"')
        expect(html).toContain('rect x="8" y="15" width="24" height="20"')
        expect(html).toContain('rect x="32" y="15" width="1" height="25"')
        expect(html).toContain('circle cx="32" cy="40" r="4"')
    })

    it("Should emit events on move_borders", () => {
        wrapper.vm.move_borders('start')
        wrapper.vm.move_borders('end')

        expect(wrapper.emitted('on_start_moving_borders')).toBeTruthy()
    })

    it("Should update end_border_moved on end_move_listener", () => {
        const event = {
            clientY: 250,
            clientX: 450
        }

        wrapper.vm.end_move_listener(event)

        expect(wrapper.vm.end_border_moved.x).toEqual(100)
        expect(wrapper.vm.end_border_moved.y).toEqual(100)
    })

    it("Should update start_border_moved on start_move_listener", () => {
        const event = {
            clientY: 225,
            clientX: 450
        }

        wrapper.vm.start_move_listener(event)

        expect(wrapper.vm.start_border_moved.x).toEqual(100)
        expect(wrapper.vm.start_border_moved.y).toEqual(100)
    })

    it("SHould not emit on_change_selection_border if new borders are not set", () => {
        wrapper.vm.on_apply_new_border()

        expect(wrapper.emitted('on_change_selection_border')).not.toBeTruthy()
    })

    it("Should emit on_change_selection_border on applying new border if new border props are set", () => {
        const start_border_moved = {
            x: 1,
            y: 1
        }
        const end_border_moved = {
            x: 10,
            y: 10
        }
        wrapper.setData({
            start_border_moved,
            end_border_moved
        })

        wrapper.vm.on_apply_new_border()

        expect(wrapper.emitted('on_change_selection_border')).toBeTruthy()
        expect(wrapper.vm.start_border_moved).toEqual(null)
        expect(wrapper.vm.end_border_moved).toEqual(null)
    })
})