<template>
  <v-container fluid>

    <slot name="triggers">
      <trigger_config :actions_list=actions_list :action="action"></trigger_config>
    </slot>
    <slot name="pre_conditions">
      <pre_conditions_config :actions_list=actions_list :action="action"></pre_conditions_config>
    </slot>
    <slot name="action_config">

    </slot>
    <slot name="completion_trigger">
      <complete_conditions_config
        :project_string_id="project_string_id"
        :actions_list=actions_list
        :action="action"></complete_conditions_config>
    </slot>
  </v-container>
</template>

<script lang="ts">
import Vue from "vue";
import axios from '../../services/customInstance';
import complete_conditions_config from './complete_conditions_config'
import pre_conditions_config from './pre_conditions_config'
import trigger_config from './trigger_config'
import {default_steps_config} from './default_steps_config'

export default Vue.extend({

    name: 'action_config_wizard_base',
    components: {
      trigger_config: trigger_config,
      pre_conditions_config: pre_conditions_config,
      complete_conditions_config: complete_conditions_config,
    },
    props: ['action', 'project_string_id', 'actions_list', 'steps_config_prop'],

    mounted() {

    },

    data() {
      return {
        is_open: true,
        search: '',
        default_steps_config: default_steps_config

      }
    },
    watch: {},
    computed: {
      steps_config: function () {
        if (this.steps_config_prop) {
          return this.steps_config_prop
        }
        return this.default_steps_config
      }
    },
    methods: {}
  }
) </script>


<style>
code {
  width: 100%;
  height: 100% !important;
}
</style>
