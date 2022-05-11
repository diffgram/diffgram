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
            <v-list dense>
                <v-list-item-group>
                    <v-list-item @click="on_delete">
                        <v-list-item-content>
                            <div class="list-item">
                                Delete
                                <v-icon> mdi-delete </v-icon>
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
    name: "text_context_menu",
    props: {
        rects: {
            type: Array,
            required: true
        }
    },
    computed: {
        position: function() {
            const last_element_index = this.rects.length - 1

            const top = this.rects[last_element_index].y + 50
            const left = this.rects[last_element_index].x + this.rects[last_element_index].width + 360

            const container_height = this.search_label ? this.search_label.length * 40 + 50 : 0

            return {
                top: top + container_height + 100 < window.innerHeight ? top : top - container_height - 50,
                left: left + 260 < window.innerWidth ? left : left - 260
            }
        }
    },
    methods: {
        on_delete: function() {
            console.log("delete")
        }
    }
})
</script>

<style scoped>
.fast-menu-element {
    position: absolute
}

.list-item {
    display: flex;
    min-width: 200px;
    width: 100%;
    flex-direction: row;
    justify-content: space-between;
    align-content: center;
}
</style>