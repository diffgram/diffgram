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
                    v-model="search_value"
                    @input="on_search_label"
                />
            </div>
            <v-list dense>
                <v-list-item-group>
                    <v-list-item 
                        v-for="(label, index) in search_label" :key="`labl+list_item${index}`" 
                        @click="on_apply_label(label)"
                    >
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
            default: null
        },
        arrow_position: {
            type: Object,
            default: null
        },
        label_list: {
            type: Array,
            required: true
        }
    },
    computed: {
        position: function() {
            if (!this.rects && !this.arrow_position) return;

            if (this.rects) {
                const last_element_index = this.rects.length - 1
    
                const top = this.rects[last_element_index].y + 50
                const left = this.rects[last_element_index].x + this.rects[last_element_index].width + 360
    
                const container_height = this.search_label ? this.search_label.length * 40 + 50 : 0
    
                return {
                    top: top + container_height + 100 < window.innerHeight ? top : top - container_height - 50,
                    left: left + 260 < window.innerWidth ? left : left - 260
                }
            } else {
                return {
                    top: this.arrow_position.y + 25,
                    left: this.arrow_position.x + 350,
                }
            }
        }
    },
    data() {
        return {
            search_value: "",
            search_label: null
        }
    },
    mounted() {
        this.$emit('remove_listeners')
        this.search_label = [...this.label_list]
        window.removeEventListener("keyup", this.on_hotkeys_listener)
        window.addEventListener("keyup", this.on_hotkeys_listener)
    },
    beforeDestroy() {
        window.removeEventListener("keyup", this.on_hotkeys_listener)
        this.$emit('add_listeners')
    },
    methods: {
        on_search_label: function(e) {
            const to_search = e.toLowerCase()
            this.search_label = [...this.label_list].filter(label => label.label.name.toLowerCase().includes(to_search))
        },
        on_apply_label: function(label) {
            if (this.rects) this.$emit('create_instance', label)
            else this.$emit('create_relation', label)
        },
        on_hotkeys_listener: function(e) {
            let key = Number(e.key)
            if (key || key === 0) {
                if (key === 0) key = 9
                else key = key - 1

                if (this.search_label && this.search_label.length > key) {
                    const label_to_set = this.search_label[key]
                    this.on_apply_label(label_to_set)
                }
            } else {
                if (e.key.length === 1) {
                    this.search_value += e.key
                } else if (e.keyCode === 8) {
                    this.search_value = this.search_value.slice(0, -1)
                }
                this.on_search_label(this.search_value)
            }
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
    min-width: 100px;
    width: 100%;
    flex-direction: row;
    justify-content: space-between;
}
</style>