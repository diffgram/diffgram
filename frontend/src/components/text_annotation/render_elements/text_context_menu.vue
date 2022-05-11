<template>
    <div 
        class="fast-menu-element"
        :style="`top: ${context_menu.y}px; left: ${context_menu.x}px`" 
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
        context_menu: {
            type: Object,
            required: true
        }
    },
    methods: {
        on_delete: function() {
            this.$emit('delete_instance', this.context_menu.instance)
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