<template>
    <g @click="on_apply_new_border">
        <circle 
            :cx="start_border_position.x"
            :cy="start_border_position.y"
            :r="4"
            :fill="solid_fill"
            class="move-cursor"
            @mousedown="move_borders('start')"
        />
        <rect
            :x="start_border_position.x"
            :y="start_border_position.y"
            :width="1"
            :height="25"
            :fill="solid_fill"
        />
        <rect
            v-for="rect in rects"
            :key="`selection_${rect.x}_${rect.y}_${rect.width}`"
            :x="rect.x - 2"
            :y="rect.y + 5"
            :width="rect.width + 4"
            :height="20"
            :fill="transparent_fill"
        />
        <rect
            :x="end_border_position.x"
            :y="end_border_position.y + 5"
            :width="1"
            :height="25"
            :fill="solid_fill"
        />
        <circle 
            :cx="end_border_position.x"
            :cy="end_border_position.y + 30"
            :r="4"
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
        }
    },
    computed: {
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
    data() {
        return {
            solid_fill: "rgba(76, 139, 245)",
            transparent_fill: "rgba(76, 139, 245, 0.4)",
            end_border_moved: null,
            start_border_moved: null
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
            this.end_border_moved = {
                x: e.clientX - 350,
                y: e.clientY - 150
            }
        },
        start_move_listener: function(e) {
            this.start_border_moved = {
                x: e.clientX - 350,
                y: e.clientY - 125
            }
        },
        on_apply_new_border: function() {
            if (!this.end_border_moved && !this.start_border_moved) return

            window.removeEventListener('mousemove', this.start_move_listener)
            window.removeEventListener('mousemove', this.end_move_listener)

            this.$emit('on_change_selection_border', this.start_border_moved, this.end_border_moved)

            this.end_border_moved = null
            this.start_border_moved = null
        }
    }
})
</script>

<style scoped>
.move-cursor {
    cursor: grab;
}
</style>
