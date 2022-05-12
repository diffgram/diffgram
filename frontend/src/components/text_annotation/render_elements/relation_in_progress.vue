<template>
    <g v-if="render_drawing_arrow">
        <circle
            :cx="render_drawing_arrow.marker.x"
            :cy="render_drawing_arrow.marker.y"
            :fill="solid_fill"
            r="3"
            class="unselectable"
        />
        <path
            v-if="render_drawing_arrow.path"
            :stroke="solid_fill"
            :d="render_drawing_arrow.path"
            fill="transparent"
            class="unselectable"
        />
        <path
            v-if="render_drawing_arrow.arrow"
            :d="`M ${render_drawing_arrow.arrow.x} ${render_drawing_arrow.arrow.y} l -5, -5 l 10, 0 l -5, 5`"
            :fill="solid_fill"
            class="unselectable"
        />
    </g>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
    name: "relation_in_progress",
    props: {
        render_drawing_arrow: {
            type: Object,
            required: true
        }
    },
    data() {
        return {
            solid_fill: "rgba(76, 139, 245)",
            end_border_moved: null,
            start_border_moved: null
        }
    },
    methods: {}
})
</script>
