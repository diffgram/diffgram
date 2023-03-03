<template>
    <g @click="on_apply_new_border">
        <circle 
            :cx="start_border_position.x"
            :cy="start_border_position.y"
            :r="circle_radius"
            :fill="solid_fill"
            class="move-cursor"
            @mousedown="move_borders('start')"
        />
        <rect
            :x="start_border_position.x"
            :y="start_border_position.y"
            :width="border_rect_width"
            :height="selection_rect_height + circle_radius"
            :fill="solid_fill"
        />
        <rect
            v-for="rect in no_empty_rects"
            :key="`selection_${rect.x}_${rect.y}_${rect.width}`"
            :x="rect.x - 2"
            :y="rect.y + circle_radius"
            :width="rect.width + circle_radius"
            :height="selection_rect_height"
            :fill="transparent_fill"
            @click="on_selection_click"
        />
        <rect
            :x="end_border_position.x"
            :y="end_border_position.y + circle_radius"
            :width="border_rect_width"
            :height="selection_rect_height + circle_radius"
            :fill="solid_fill"
        />
        <circle 
            :cx="end_border_position.x"
            :cy="end_border_position.y + selection_rect_height + 2 * circle_radius"
            :r="circle_radius"
            :fill="solid_fill"
            class="move-cursor"
            @mousedown="move_borders('end')"
        />
    </g>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
    name: "text_selection_svg",
    props: {
        rects: {
            type: Array,
            required: true
        },
        svg_ref: {
            type: SVGSVGElement,
            required: true
        }
    },
    data() {
        return {
            solid_fill: "rgba(76, 139, 245)",
            transparent_fill: "rgba(76, 139, 245, 0.4)",
            end_border_moved: null,
            start_border_moved: null,
            circle_radius: 5,
            border_rect_width: 1,
            selection_rect_height: 20
        }
    },
    computed: {
        no_empty_rects: function() {
            return this.rects.filter(rect => rect.x && rect.y && rect.width)
        },
        last_element: function() {
            const index = this.rects.length - 1
            return index
        },
        end_border_position: function() {
            if (!this.end_border_moved) return {
                x: this.rects[this.last_element].width + 2 + this.rects[this.last_element].x,
                y: this.rects[this.last_element].y
            }

            return {
                x: this.end_border_moved.x,
                y: this.end_border_moved.y
            }
        },
        start_border_position: function() {
            if (!this.start_border_moved) return {
                x: this.rects[0].x - 2,
                y: this.rects[0].y
            }

            return {
                x: this.start_border_moved.x,
                y: this.start_border_moved.y
            }
        }
    },
    methods: {
        move_borders: function(direction) {
            this.$emit('on_start_moving_borders')
            if (direction === 'start') {
                window.addEventListener('mousemove', this.start_move_listener)
            } else {
                window.addEventListener('mousemove', this.end_move_listener)
            }
        },
        end_move_listener: function(e) {
            const element_bounding_box = this.svg_ref.getBoundingClientRect()
            this.end_border_moved = {
                x: e.clientX - element_bounding_box.left,
                y: e.clientY - element_bounding_box.top - 2 * (this.selection_rect_height + this.circle_radius)
            }
        },
        start_move_listener: function(e) {
            const element_bounding_box = this.svg_ref.getBoundingClientRect()
            this.start_border_moved = {
                x: e.clientX - element_bounding_box.left,
                y: e.clientY - element_bounding_box.top - this.selection_rect_height - this.circle_radius
            }
        },
        on_apply_new_border: function() {
            if (!this.end_border_moved && !this.start_border_moved) return

            window.removeEventListener('mousemove', this.start_move_listener)
            window.removeEventListener('mousemove', this.end_move_listener)

            this.$emit('on_change_selection_border', this.start_border_moved, this.end_border_moved)

            this.end_border_moved = null
            this.start_border_moved = null
        },
        on_selection_click: function(e) {
            this.$emit('on_selection_click', e)
        }
    }
})
</script>

<style scoped>
.move-cursor {
    cursor: grab;
}
</style>
