<template>
  <div class="d-flex">
    <v-select return-object
              v-model="action"
              item-value="type"
              item-text="name"
              :items="actions_list" @change="set_action">

    </v-select>
    <v-btn icon outlined><v-icon>mdi-cog</v-icon></v-btn>
  </div>
</template>

<script lang="ts">

import Vue from 'vue';
import label_schema_selector from '../label/label_schema_selector.vue'
import button_edit_workflow_creator from './button_workflow_editor.vue'
import attribute_select from '../attribute/attribute_select.vue'

import {types} from "sass";
import String = types.String;
import {attribute_group_list} from "../../services/attributesService";

export default Vue.extend({
  name: 'ButtonEditContextMenu',
  components: {
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
      await this.initialize_button_action_config(this.existing_action)
    }
  },
  data() {
    // move context menu off the page out of view when hidden
    return {
      action: null,
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
    initialize_existing_action: function (existing_action) {
      this.action = existing_action;
    },
    set_action: function () {

    },

  }
});
</script>

<style>
.custom-text-field {
  font-size: 16px;
}
</style>
