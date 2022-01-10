<template>
<g 
    class="cursor" 
    @mouseover="on_relation_hover"
    @mouseout="on_relation_stop_hover"
>
    <circle :cx="relation.start_marker.x" :cy="relation.start_marker.y" r="3" :fill="current_color"/>
    <path 
        :d="relation_arrow_path" 
        :fill="current_color" 
    />
    <path
        fill="transparent"
        v-for="relation_path in relation_paths"
        :key="relation_path"
        :d="relation_paths" 
        :stroke="current_color" 
    />
    <text
        class="annotation-font-size"
        :x="relation.M1" 
        :y="relation.M2 - 15" 
        :stroke="current_color" 
    >
        {{ relation.label.label.name }}
    </text>
</g>
</template>

<script>
import Vue from 'vue'

export default Vue.extend({
    name: "text_relation",
    props: {
        relation: {
            type: Object,
            required: true
        },
        relation_hover: {
            type: Object,
            default: {}
        }
    },
    methods: {
        on_relation_hover: function() {
            this.$emit('on_relation_hover', this.relation.id)
        },
        on_relation_stop_hover: function() {
            this.$emit('on_relation_stop_hover')
        }
    },
    computed: {
        current_color: function() {
            return this.relation_hover.relation_hover_id === this.relation.id ? 'red' : this.relation.label.colour.hex
        },
        relation_paths: function() {
            const paths = this.relation.relationItems.map(path_item => `M ${path_item.M1} ${path_item.M2} v -10 H ${path_item.H} v 10`)
            return paths
        },
        relation_arrow_path: function() {
            const { x, y } = this.relation.end_marker
            return `M ${x} ${y} l -5, -5 l 10, 0 l -5, 5`
        }
    }
})
</script>

<style scoped>
.cursor {
    cursor: pointer;
}

.annotation-font-size {
    font-size: 10px !important;
}
</style>
