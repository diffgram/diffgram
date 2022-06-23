<template>
  <v-container fluid>

    <slot name="triggers" :action_template="action_template">
      <trigger_config
        :action_template="action_template"
        :project_string_id="project_string_id"
        :actions_list=actions_list
        :action="action"></trigger_config>
    </slot>
    <slot name="pre_conditions">
      <pre_conditions_config
        :action_template="action_template"
        :project_string_id="project_string_id"
        :actions_list=actions_list
        :action="action">

      </pre_conditions_config>
    </slot>
    <slot name="action_config">

    </slot>
    <slot name="completion_trigger">
      <complete_conditions_config
        :project_string_id="project_string_id"
        :actions_list=actions_list
        :action_template="action_template"
        :action="action">

      </complete_conditions_config>
    </slot>
  </v-container>
</template>

<script lang="ts">
import Vue from "vue";
import complete_conditions_config from './complete_conditions_config.vue'
import pre_conditions_config from './pre_conditions_config.vue'
import trigger_config from './trigger_config.vue'

export default Vue.extend({
    name: 'action_config_wizard_base',
    components: {
      trigger_config: trigger_config,
      pre_conditions_config: pre_conditions_config,
      complete_conditions_config: complete_conditions_config,
    },
    props: [
      'action', 
      'project_string_id', 
      'actions_list', 
      'steps_config', 
      'action_template'
    ],
    data() {
      return {
        is_open: true,
        search: ''
      }
    },
  }
) </script>


<style>
code {
  width: 100%;
  height: 100% !important;
}
</style>
