<template>
  <v-menu  persistent
           :close-on-click="false"
           :close-on-content-click="false"
           :offset-overflow="true"
           :position-x="150"
           :position-y="50"
           :right="true"
           offset-y
           v-if="button"
           v-model="open">
      <v-card class="pa-4">
        <v-card-text>
          <v-tabs
            v-model="tab"
            @change="on_change_tab"
            background-color="#f0f0f0"
          >
            <v-tabs-slider color="secondary"></v-tabs-slider>

            <v-tab
              style="border-bottom: 1px solid #e0e0e0"
              v-for="item in ['Style', 'Actions']"
              :key="item"
            >
              {{ item }}
            </v-tab>
            <v-tabs-items v-model="tab">
              <v-tab-item :key="1">
                <div class="d-flex flex-column">
                  <v-text-field class="custom-text-field" label="Button Title" v-model="button.display_name"></v-text-field>
                  <slider-picker class="mb-4" v-model="button_color" @change="change_color"/>
                </div>
              </v-tab-item>
              <v-tab-item :key="2">
                <h4 class="">Actions: </h4>

                <v-select return-object
                          v-model="action"
                          item-value="type"
                          item-text="name"
                          :items="actions_list" @change="set_action"></v-select>

                <label_schema_selector
                  v-if="action && action.type === 'set_attribute'"
                  @change="on_change_schema"
                  :project_string_id="project_string_id">

                </label_schema_selector>
                <attribute_select
                  ref="attribute_select"
                  :multiple="false"
                  label="Select Attribute to set"
                  v-if="selected_schema_id"
                  :project_string_id="project_string_id"
                  :schema_id="selected_schema_id"
                  :attribute_list="attribute_list"
                  @change_selected="attribute_change_event"
                  @attribute_change="attribute_change_value"
                />
              </v-tab-item>
            </v-tabs-items>
          </v-tabs>
        </v-card-text>


        <v-card-actions class="d-flex justify-end">
          <v-btn color="primary" @click="close_menu">
            Close
          </v-btn>
          <v-btn color="success" @click="save">
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
  </v-menu>

</template>

<script lang="ts">

import Vue from 'vue';
import label_schema_selector from '../label/label_schema_selector.vue'
import attribute_select from '../attribute/attribute_select.vue'
import axios from '../../services/customInstance';
import {ActionCustomButton} from '../../types/ui_schema/Buttons'
import {types} from "sass";
import String = types.String;
import {attribute_group_list} from "../../services/attributesService";
export default Vue.extend({
  name: 'ButtonEditContextMenu',
  components: {
    label_schema_selector,
    attribute_select
  },
  props: {
    'project_string_id': {type: String, required: true},
    'button': {
      required: true,

    }

  },
  mounted: async function(){
    if(this.button && this.button.action){
      await this.initialize_button_action_config()
    }
  },
  data() {
    // move context menu off the page out of view when hidden
    return {
      button_color: {},
      tab: 0,
      selected_schema_id: undefined,
      actions_list: [
        {
          'name': 'Complete Task',
          'type': 'complete_task',
        },
        {
          'name': 'Set Attribute',
          'type': 'set_attribute',
        },

      ],
      open: false,
      action: null,
      label_schema: null,
      attribute_value: null,
      attribute_list: [],
    }
  },
  watch:{
    button: {
      handler: function (val){
        this.tab = 0
        this.initialize_button_action_config()
      },
    },
    button_color: {
      deep: true,
      handler: function(val){
        this.button.color = val.hex
      }
    },

  },
  computed: {
  },
  methods: {
    initialize_button_action_config: async function(){
      if(this.button.action){
        this.set_action(new ActionCustomButton(this.button.action.name, this.button.action.type, this.button.action.metadata))

      }
      let attr_template_id = this.button.action.metadata.attribute_template_id
      if(this.button.action.metadata.schema_id){
        this.selected_schema_id = this.button.action.metadata.schema_id
      }
      if(attr_template_id){
        await this.get_schema_attributes()
        await this.$nextTick();
        const attr_select = this.$refs.attribute_select;
        if(!attr_select){
          return
        }
        await attr_select.select_attribute_by_id(attr_template_id)
        const attr_value_id = this.button.action.metadata.attribute_value_id
        await this.$nextTick();
        if(attr_value_id){
          const attr_list_ref = attr_select.$refs.attribute_groups_list

          const attr_ref = attr_list_ref.$refs[`attribute_group_${attr_template_id}`]

          if(attr_ref && attr_ref.length > 0){
            attr_ref[0].set_attribute_value(attr_value_id)
          }
        }
      }
    },
    set_action: function(val){
      this.action = new ActionCustomButton(val.name, val.type, val.metadata? val.metadata: {});
      this.button.action = this.action
    },
    open_menu: function(){
      this.open = true
    },
    close_menu: function(){
      this.open = false;
    },
    change_color: function(val){
      this.button.color = val
    },
    on_change_tab: async function(tab){
      if(tab === 1){
        await this.initialize_button_action_config()
      }
    },
    save: async function(){
      await this.$store.commit('update_custom_button', this.button.name, this.button)
      await this.update_ui_schema_with_servercall()
      this.open = false

    },
    get_ui_schema: function () {
      if (this.$store.state.ui_schema.current == undefined) {
        throw new Error("this.$store.state.ui_schema.current is undefined")
      }
      return this.$store.state.ui_schema.current
    },
    on_change_schema: async function(val){
      this.selected_schema_id = val.id
      if(this.action){
        this.action.set_metadata('schema_id', val.id)
      }
      this.label_schema = val
      await this.get_schema_attributes()
    },
    get_schema_attributes: async function () {
      const [data, error] = await attribute_group_list(this.project_string_id, undefined, this.selected_schema_id, 'from_project')

      if (!error) {
        this.attribute_list = [...data.attribute_group_list]
      }
    },
    attribute_change_value: function(attr_value_payload){
      let attribute_template = attr_value_payload[0]
      let attribute_selected_value = attr_value_payload[1]
      this.action.set_metadata('attribute_value_id', attribute_selected_value.id)
      this.attribute_value = attribute_selected_value
    },
    attribute_change_event: function(attr){
      this.action.set_metadata('attribute_template_id', attr.id)
      this.attribute = attr
    },
    update_ui_schema_with_servercall: async function(){
      if (!this.get_ui_schema() || !this.get_ui_schema().id) {
        return
      }

      this.loading = true;
      this.error = {}

      try{
        const response = await axios.post(
          `/api/v1/project/${this.project_string_id}/ui_schema/update`,
          this.get_ui_schema()
        )
      }
      catch (error) {
        this.error = this.$route_api_errors(error)
        console.error(error)

      }
      finally {
        this.loading = false;
      }

    },
  }
});
</script>

<style>
.custom-text-field {
  font-size: 16px;
}
</style>
