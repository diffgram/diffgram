<template>
    <div 
        class="fast-menu-element"
        :style="`top: ${position.top}px; left: ${position.left}px`" 
    >
        <v-card
            class="mx-auto"
            max-width="400"
            tile
        >
            <div style="padding: 0px 5px">
                <v-text-field
                    label="Start by typing label name"
                    hide-details="auto"
                />
            </div>
            <v-list dense>
                <v-list-item-group>
                    <v-list-item v-for="(label, index) in label_list" :key="`labl+list_item${index}`">
                        <v-list-item-content>
                            <div class="list-item" :style="`color: ${label.colour.hex}`">
                                {{ label.label.name }} 
                                <kbd>{{ index + 1 }}</kbd>
                            </div>
                        </v-list-item-content>
                    </v-list-item>
                </v-list-item-group>
            </v-list>
        </v-card>
    </div>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
    name: "text_fast_label",
    props: {
        rects: {
            type: Array,
            required: true
        },
        label_list: {
            type: Array,
            required: true
        }
    },
    computed: {
        position: function() {
            const last_element_index = this.rects.length - 1

            const top = this.rects[last_element_index].y + 50
            const left = this.rects[last_element_index].x + this.rects[last_element_index].width + 360
            return {
                top,
                left
            }
        }
    },
    data() {
        return {}
    },
})
</script>

<style scoped>
.fast-menu-element {
    position: absolute
}

.list-item {
    display: flex;
    min-width: 100px;
    width: 100%;
    flex-direction: row;
    justify-content: space-between;
}
</style>