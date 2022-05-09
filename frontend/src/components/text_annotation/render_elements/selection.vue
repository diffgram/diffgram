<template>
    <g>
        <circle 
            :cx="rects[0].x - 2"
            :cy="rects[0].y"
            :r="4"
            :fill="solid_fill"
            class="move-cursor"
        />
        <rect
            :x="rects[0].x - 2"
            :y="rects[0].y"
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
            :x="rects[last_element].width + 2 + rects[last_element].x"
            :y="rects[last_element].y + 5"
            :width="1"
            :height="25"
            :fill="solid_fill"
        />
        <circle 
            :cx="rects[last_element].width + 2 + rects[last_element].x"
            :cy="rects[last_element].y + 30"
            :r="4"
            :fill="solid_fill"
            class="move-cursor"
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
        }
    },
    data() {
        return {
            solid_fill: "rgba(46, 204, 113)",
            transparent_fill: "rgba(46, 204, 113, 0.4)"
        }
    },
    methods: {}
})
</script>

<style scoped>
.move-cursor {
    cursor: grab;
}
</style>
