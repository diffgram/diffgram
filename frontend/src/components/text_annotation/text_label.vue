<template>
    <g
        @mouseover="on_annotation_hover"
        @mouseout="on_stop_hover"
        @mousedown.prevent="on_add_relation"
    >
        <rect 
            v-for="labelItem in annotation.labelItems"
            height="20" 
            class="cursor"
            opacity="0.4"
            :x="labelItem.x" 
            :y="labelItem.y" 
            :width="labelItem.width"
            :fill="current_color"
        />
        <text 
            class="annotation-font-size"
            :x="annotation.x" 
            :y="annotation.y + 30" 
            :stroke="current_color"
        >
            {{ annotation.label.label.name }}
        </text>
    </g>
</template>

<script>
import Vue from 'vue'

export default Vue.extend({
    name: "text_label",
    props: {
        annotation: {
            type: Object,
            reqired: true
        },
        hover_id: {
            type: Number,
            default: null
        },
        relation_hover: {
            type: Object,
            default: {}
        },
        sentence_index: {
            type: Number,
            reqired: true
        }
    },
    computed: {
        current_color: function() {
            const set_annotation_color = 
                this.hover_id === this.annotation.id || 
                this.relation_hover.start_label_id === this.annotation.id || 
                this.relation_hover.end_label_id === this.annotation.id ? 
                'red' : 
                this.annotation.label.colour.hex
            return set_annotation_color
        }
    },
    methods: {
        on_annotation_hover: function() {
            this.$emit('on_annotation_hover', this.annotation.id)
        },
        on_stop_hover: function() {
            this.$emit('on_stop_hover')
        },
        on_add_relation: function(event) {
            this.$emit('on_add_relation',event, this.sentence_index, this.annotation.id)
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
