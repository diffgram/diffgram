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
            <div class="context-header">
                Label: 
                <strong :style="`color: ${context_menu.instance.label_file.colour.hex}`">
                    {{ context_menu.instance.label_file.label.name }}
                </strong>
                <br />
                {{ display_attributes ? `Attributes: ${display_attributes}` : null }}
            </div>
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
    computed: {
        display_attributes: function() {
            if (!this.context_menu || !this.context_menu.instance || !this.context_menu.instance.attribute_groups) return null

            const attribute_keys = Object.keys(this.context_menu.instance.attribute_groups)

            let attribute_string = ""

            attribute_keys.map(attribute_key => {
                attribute_string += this.context_menu.instance.attribute_groups[attribute_key].display_name + ', '
            })
            
            return attribute_string.slice(0, -2)
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

.context-header {
    padding: 16px;
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