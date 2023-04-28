<template>
  <div>
    <div v-if="button.workflow && button.workflow.actions_list && button.actions_list.length > 0" v-for="action in button.actions_list">
      <button_edit_action_step
        :project_string_id="project_string_id"
        :button="button"
        :existing_action="action">
      </button_edit_action_step>
    </div>
    <div v-else>
      <p>No Actions yet. Add an action to make your button do something!</p>
      <v-icon size="48">gesture-tap</v-icon>
    </div>
    <div class="d-flex justify-end">
      <v-btn @click="add_action" color="secondary" x-small><v-icon>mdi-plus</v-icon>Add Action</v-btn>
    </div>

  </div>
</template>

<script lang="ts">

import Vue from 'vue';
import label_schema_selector from '../label/label_schema_selector.vue'
import button_edit_workflow_creator from './button_workflow_editor.vue'
import button_edit_action_step from './button_edit_action_step'
import attribute_select from '../attribute/attribute_select.vue'

import {types} from "sass";
import String = types.String;
import {attribute_group_list} from "../../services/attributesService";
export default Vue.extend({
  name: 'button_workflow_editor',
  components: {
    label_schema_selector,
    button_edit_workflow_creator,
    button_edit_action_step,
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
  methods: {
    add_action: function(){

    },

  }
});
</script>

<style>
.custom-text-field {
  font-size: 16px;
}
</style>
