<template>
  <div class="sidebar">
    <v-expansion-panels multiple accordion :value="[0]">
        <v-expansion-panel 
            data-cy="instance-expansion-panel" 
        >
            <v-expansion-panel-header>
                <strong>Instances</strong>
            </v-expansion-panel-header>
            
            <v-expansion-panel-content>
                <v-data-table
                    hide-default-footer
                    :style="`width: 350px; max-height: 100%; overflow-y: scroll`"
                    :headers="headers"
                    :items="instance_list"
                    fixed-header
                    disable-pagination
                    single-select
                >
                    <template v-slot:body="{ items }">
                        <tbody 
                            v-if="items.length > 0 && !loading" 
                            style="cursor: pointer"
                        >
                            <tr
                                v-for="(item, item_index) in items"
                                :key="item.id"
                                :style="current_instance && current_instance.id === item.id && 'background-color: #ecf0f1'"
                                @mouseover="on_hover_item(item)"
                                @mouseleave="on_stop_hover_item"
                                @click="on_select_instance(item)"
                            >
                                <td 
                                    v-if="$store.state.user.settings.show_ids == true" 
                                    class="centered-table-items"
                                >
                                    {{ item.id || 'new' }}
                                </td>

                                <td class="centered-table-items">
                                    <v-icon 
                                        v-if="item.type === 'relation'"
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
                                
                                <td 
                                    :data-cy="`label_name_${item_index}`" 
                                    class="centered-table-items"
                                >
                                    {{ item.label_file.label.name }}
                                </td>

                                <td class="centered-table-items">
                                    <v-layout justify-center>
                                        <button_with_menu
                                            tooltip_message="Change Label Template"
                                            icon="mdi-format-paint"
                                            color="primary"
                                            :datacy="`change_label_${item_index}`"
                                            :close_by_button="true"
                                        >
                                            <template slot="content">
                                                <label_select_only
                                                    :label_file_list_prop="label_list"
                                                    :select_this_id_at_load="item.label_file_id"
                                                    datacy="select_text_label"
                                                    @label_file="$emit('change_instance_label', { label: $event, instance: item })"
                                                />
                                            </template>
                                        </button_with_menu>

                                        <standard_button
                                            color="primary"
                                            icon="mdi-delete"
                                            tooltip_message="Delete instance"
                                            @click.stop="$emit('delete_instance', item)"
                                            :icon_style="true"
                                            :bottom="true"
                                        />
                                    </v-layout>
                                </td>
                            </tr>
                        </tbody>
                                
                        <tbody v-else>
                            <tr>
                                <td 
                                    :colspan="headers.length" 
                                    style="text-align: center"
                                >
                                    {{ loading ? "Loading..." : "No instances have been created yet" }}
                                </td>
                            </tr>
                        </tbody>
                    </template>
                </v-data-table>
            </v-expansion-panel-content>
        </v-expansion-panel>
    </v-expansion-panels>
  </div>
</template>

<script lang="ts">
import Vue from "vue";

export default Vue.extend({
  name: "sidebar",
  props: {
    project_string_id: {
      type: String,
      required: true
    },
  },
	data() {
		return {
			instance_list: [] as Array<Object>,
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
            ]
		}
	}
})
</script>

<style scoped>
.sidebar {
    width: 300px;
    height: calc(100vh - 75px);
    border-right: 1px solid rgba(0,0,0,.12);
}
</style>
