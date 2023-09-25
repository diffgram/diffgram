<template>
    <div
        class="wrapper-element"
        :style="`
            height: ${sidebar_height}px
            top: ${toolbar_height}
        `"
    >
        <v-expansion-panels multiple style="width: 450px;" accordion :value="open_panels">
            <v-expansion-panel @change="on_change_expansion(0)">
              <global_attributes_list
                v-if="annotation_ui_context.global_attribute_groups_list_compound && annotation_ui_context.global_attribute_groups_list_compound.length > 0"
                :global_attribute_groups_list="annotation_ui_context.global_attribute_groups_list_compound"
                :current_global_instance="compound_global_instance"
                :schema_id="schema_id"
                :project_string_id="project_string_id"
                :view_only_mode="false"
                :title="'Compound Files Attribute'"
                ref="compound_attributes_list"
                @attribute_change="compound_global_attribute_change($event)"
            />
        </v-expansion-panel>

          <v-expansion-panel @change="on_change_expansion(1)">
              <global_attributes_list
                v-if="global_attribute_groups_list && global_attribute_groups_list.length > 0"
                :project_string_id="project_string_id"
                :global_attribute_groups_list="global_attribute_groups_list"
                :current_global_instance="current_global_instance()"
                :schema_id="schema_id"
                :view_only_mode="false"
                ref="global_attributes_list"
                @attribute_change="attribute_change($event, true)"
              />
          </v-expansion-panel>

            <v-expansion-panel @change="on_change_expansion(2)" :disabled="!current_instance">

                <v-expansion-panel-header>
                    <strong>Attributes {{ !current_instance ? "(select instance)" : null }}</strong>
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                    <attribute_group_list
                        :project_string_id="project_string_id"
                        v-if="attribute_group_list_prop().length !== 0 || (current_instance && current_instance.attribute_groups)"
                        :mode="'annotate'"
                        :view_only_mode="false"
                        :schema_id="schema_id"
                        :attribute_group_list_prop="attribute_group_list_prop()"
                        :current_instance="current_instance"
                        @attribute_change="attribute_change($event)"
                        ref="attributes_list"
                        key="attribute_groups_list"
                    />
                </v-expansion-panel-content>
            </v-expansion-panel>
            <v-expansion-panel data-cy="instance-expansion-panel" @change="on_change_expansion(3)">
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
                                <tbody v-if="items.length > 0 && !loading" style="cursor: pointer">
                                <tr
                                    v-for="(item, item_index) in items"
                                    :key="item.id"
                                    @mouseover="on_hover_item(item)"
                                    @mouseleave="on_stop_hover_item"
                                    @click="on_select_instance(item)"
                                    :style="current_instance && current_instance.id === item.id && 'background-color: #ecf0f1'"
                                >
                                    <td v-if="$store.state.user.settings.show_ids == true" class="centered-table-items">
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
                                    <td :data-cy="`label_name_${item_index}`" class="centered-table-items">
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
                                        <td :colspan="headers.length" style="text-align: center">
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
import Vue from 'vue'
import instance_detail_list_view from "../image_and_video_annotation/instance_detail_list_view.vue";
import button_with_menu from '../../regular/button_with_menu.vue';
import label_select_only from '../../label/label_select_only.vue'
import attribute_group_list from '../../attribute/attribute_group_list.vue'
import global_attributes_list from '../../attribute/global_attributes_list.vue'


export default Vue.extend({
    name: "text_sidepanel",
    components: {
        instance_detail_list_view,
        button_with_menu,
        label_select_only,
        attribute_group_list,
        global_attributes_list
    },
    props: {
        sidebar_height: {type: Number, required: true},
        project_string_id: {
            type: String,
            required: true
        },
        schema_id: {
            type: Number,
            required: true
        },
        per_instance_attribute_groups_list: {
            type: Array,
            default: []
        },
        current_instance: {
            type: Object,
            default: null
        },
        instance_list: {
            type: Array,
            default: []
        },
        label_list: {
            type: Array,
            default: []
        },
        toolbar_height: {
            type: String,
            default: '0px'
        },
        loading: {
            type: Boolean,
            required: true
        },
        global_attribute_groups_list: {
            type: Array,
            default: null
        },
        annotation_ui_context: {
            type: Object,
            required: true
        },
        compound_global_instance: {
            type: Object,
            default: () => {}
        },
    },
    data() {
        return {
            open_panels: [0, 1]
        }
    },
    computed: {
        headers: function() {
            if (this.$store.state.user.current.is_super_admin) {
                return [
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

            return [
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
    },
    methods: {
        on_change_expansion: function(panel_index) {
            if (!this.open_panels.includes(panel_index)) this.open_panels.push(panel_index)
            else {
                const index_to_remove = this.open_panels.indexOf(panel_index)
                this.open_panels.splice(index_to_remove, 1)
            }
        },
        on_hover_item: function(item) {
            this.$emit("on_instance_hover", item.get_instance_data().id)
        },
        on_stop_hover_item: function() {
            this.$emit("on_instance_stop_hover")
        },
        on_select_instance: function(instance) {
            this.$emit("on_select_instance", instance)
        },
        attribute_group_list_prop: function () {

            if (!this.label_list
                || !this.current_instance
                || !this.per_instance_attribute_groups_list
                || !this.current_instance.label_file) {
                    return []
            }

            let attr_group_list = this.per_instance_attribute_groups_list.filter(elm =>{
                let file_id_list = elm.label_file_list.map(label_file => label_file.id)
                return file_id_list.includes(this.current_instance.label_file.id)
            })

            return attr_group_list;
      },
      attribute_change: function(event, is_global = false) {
          this.$emit('on_update_attribute', event, is_global)
      },
      compound_global_attribute_change: function(attribute){
        this.$emit('global_compound_attribute_change', attribute)
      },
      current_global_instance: function() {
        if (this.annotation_ui_context.instance_store && this.annotation_ui_context.instance_store.instance_store[this.annotation_ui_context.working_file.id]) {
            const global_instance = this.annotation_ui_context.instance_store.instance_store[this.annotation_ui_context.working_file.id].global_instance

            return global_instance
        }
        return null
      }
    }
})
</script>

<style scoped>
.wrapper-element {
    width: 450px;
    min-width: 450px;
    border-right: 1px solid #e0e0e0;
    position: sticky;
    left: 0;
    overflow: scroll;
}

.centered-table-items {
    vertical-align: middle;
    text-align: center;
}
</style>
