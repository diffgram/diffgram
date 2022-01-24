<template>
    <div style="width: 350px; border-right: 1px solid grey;">
        <v-data-table
            style="width: 350px"
            hide-default-footer
            :headers="headers"
            :items="instance_list"
        >
            <template v-slot:body="{ items }">
                <tbody v-if="items.length > 0">
                  <tr
                    v-for="item in items"
                    :key="item.id"
                    @mouseover="on_hover_item(item)"
                    @mouseleave="on_stop_hover_item"
                  >
                    <td class="centered-table-items">
                        {{ item.id }}
                    </td>
                    <td class="centered-table-items">
                        <v-icon 
                            v-if="item.type === 'text_relation'"
                            :color="item.label_file.colour.hex"
                        >
                            mdi-relation-one-to-one
                        </v-icon>
                        <v-icon 
                            v-if="item.type === 'text_token'"
                            :color="item.label_file.colour.hex"
                        >
                            mdi-label
                        </v-icon>
                    </td>
                    <td class="centered-table-items">
                        {{ item.label_file.label.name }}
                    </td>
                    <td class="centered-table-items">
                        <button_with_menu
                                tooltip_message="Change Label Template"
                                icon="mdi-format-paint"
                                color="primary"
                                :close_by_button="true"
                              >

                                <template slot="content">
                                    <label_select_annotation
                                        :project_string_id="project_string_id"
                                        :label_file_list="label_list"
                                        :label_file_colour_map="label_file_colour_map"
                                        :loading="loading"
                                        :request_refresh_from_project="true"
                                        :show_visibility_toggle="true"
                                        @change="$emit('change_label_file', $event)"
                                        @update_label_file_visible="$emit('update_label_file_visibility', $event)"
                                    />
                                </template>
                        </button_with_menu>
                    </td>
                  </tr>
                </tbody>
                <tbody v-else>
                    <tr>
                        <td :colspan="headers.length" style="text-align: center">No instances have been created yet</td>
                    </tr>
                </tbody>
            </template>
        </v-data-table>
    </div>
</template>

<script lang="ts">
import Vue from 'vue'
import instance_detail_list_view from "../annotation/instance_detail_list_view.vue";
import button_with_menu from '../regular/button_with_menu.vue';
import label_select_annotation from "../label/label_select_annotation.vue"

export default Vue.extend({
    name: "text_sidepanel",
    components: {
        instance_detail_list_view,
        button_with_menu,
        label_select_annotation
    },
    props: {
        instance_list: {
            type: Array,
            default: []
        }
    },
    data() {
        return {
            headers: [
                {
                    text: 'Id',
                    align: 'center',
                    sortable: false,
                    value: 'id'
                },
                {
                    text: 'Type',
                    align: 'center',
                    sortable: false,
                    value: 'type'
                },
                { 
                    text: 'Name', 
                    value: 'label_file.label.name',
                    sortable: false,
                    align: 'center'
                },
                { 
                    text: 'Action', 
                    value: 'action',
                    sortable: false,
                    align: 'center'
                }
            ],
        }
    },
    methods: {
        on_hover_item: function(item) {
            this.$emit("on_instance_hover", item.id)
        },
        on_stop_hover_item: function() {
            this.$emit("on_instance_stop_hover")
        }
    }
})
</script>

<style scoped>
.centered-table-items {
    vertical-align: middle; 
    text-align: center;
}
</style>