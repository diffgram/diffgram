<template>
  <div class="d-flex align-center justify-start">
    <v-select return-object
              v-model="action"
              item-value="type"
              item-text="name"
              :items="actions_list" @change="set_action">

    </v-select>
    <v-btn @click="open_config_dialog" :disabled="!action || (action && !action.type)" small class="ml-4" icon outlined><v-icon>mdi-cog</v-icon></v-btn>
    <v-btn @click="delete_action(initialized_action)" small class="ml-4" color="error" icon outlined><v-icon>mdi-delete</v-icon></v-btn>

    <v-dialog persistent  max-width="600px" v-model="is_open">
      <v-card>
        <v-card-title>Configure: </v-card-title>
        <v-card-text>
          <action_config_renderer :action="initialized_action" :project_string_id="project_string_id"></action_config_renderer>
        </v-card-text>
        <v-card-actions class="d-flex justify-end">
          <v-btn @click="is_open = false" color="success"><v-icon>mdi-content-save-check</v-icon>Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">

import Vue from 'vue';
import label_schema_selector from '../label/label_schema_selector.vue'
import button_edit_workflow_creator from './button_workflow_editor.vue'
import attribute_select from '../attribute/attribute_select.vue'
import {
  get_initialize_action_from_obj,
  get_initialized_action_from_obj
} from '../../types/ui_schema/CustomButtonWorkflow'
import {types} from "sass";
import String = types.String;
import {attribute_group_list, } from "../../services/attributesService";
import Action_config_renderer from "./action_configs/action_config_renderer.vue";

export default Vue.extend({
  name: 'button_edit_action_step',
  components: {
    Action_config_renderer,
    label_schema_selector,
    button_edit_workflow_creator,
    attribute_select
  },
  props: {
    'project_string_id': {type: String, required: true},
    'button': {required: true},
    'existing_action': {required: false},


  },
  mounted: async function () {
    if (this.existing_action) {
      await this.initialize_existing_action(this.existing_action)
    }
  },
  data() {
    // move context menu off the page out of view when hidden
    return {
      action: null,
      initialized_action: null,
      action_id: null,
      is_open: false,
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
    }
  },

  computed: {},
  methods: {
    delete_action: function(action){
      if(!this.button.workflow){
        return
      }
      this.button.workflow.remove_action(action)
    },
    initialize_existing_action: function (existing_action) {

      this.initialized_action = this.button.workflow.get_action(existing_action)
      this.action = this.initialized_action
      this.action_id = this.initialized_action.id
    },
    set_action: function (action) {

      this.action = action
      if(this.action_id){
        this.action.id = this.action_id
      }
      this.initialized_action = get_initialized_action_from_obj(this.action)
      this.button.workflow.update_action(this.initialized_action)
    },
    open_config_dialog: function(action){
      this.is_open = true;
    }

  }
});
</script>

<style>
.custom-text-field {
  font-size: 16px;
}
</style>
