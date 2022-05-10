<template>
  <v-stepper  v-model="step" style="height: 100%" @change="on_change_step">
    <v-stepper-items style="height: 100%">
      <v_error_multiple :error="error"></v_error_multiple>

      <v-stepper-content
        v-for="(keyStep, index) in Object.keys(visible_steps)"
        :step="visible_steps[keyStep].number">
        <slot :name="keyStep" v-if="keyStep === 'action_config'">

        </slot>
        <slot :name="keyStep" v-if="keyStep === 'triggers'">
          <trigger_config :actions_list=actions_list :action="action"></trigger_config>
        </slot>
        <slot :name="keyStep" v-if="keyStep === 'pre_conditions'">
          <pre_conditions_config :actions_list=actions_list :action="action"></pre_conditions_config>
        </slot>
        <slot :name="keyStep" v-if="keyStep === 'completion_trigger'">
          <complete_conditions_config
            :project_string_id="project_string_id"
            :actions_list=actions_list
            :action="action"></complete_conditions_config>
        </slot>
        <wizard_navigation
          @next="on_next_button_click"
          :next_visible="true"
          :loading_next="loading_steps"
          :disabled_next="loading_steps"
          @back="on_prev_button_click"
          :skip_visible="false">

        </wizard_navigation>
      </v-stepper-content>
      <v-stepper-content :step="Object.keys(visible_steps).length + 1">
        <slot name="sucess_config">
          <v-container class="d-flex flex-column justify-center align-center">
            <v-icon color="success" size="256">mdi-check</v-icon>
            <h1>Action Configured Sucessfully.</h1>
          </v-container>
          <wizard_navigation
            @next="on_next_button_click"
            :next_visible="false"
            :loading_next="loading_steps"
            :disabled_next="loading_steps"
            @back="on_prev_button_click"
            :skip_visible="false">

          </wizard_navigation>
        </slot>
      </v-stepper-content>

    </v-stepper-items>
    <v-stepper-header class="ma-0 pl-8 pr-8">
      <template v-for="(key, index) in Object.keys(visible_steps)">
        <v-stepper-step
          :complete="step > visible_steps[key].number"
          :step="visible_steps[key].number"
        >
          {{ visible_steps[key].header_title }}
        </v-stepper-step>
        <v-divider v-if="index < Object.keys(visible_steps).length - 1"></v-divider>
      </template>
    </v-stepper-header>
  </v-stepper>
</template>

<script lang="ts">
import Vue from "vue";
import axios from '../../services/customInstance';
import {default_steps_config} from './default_steps_config'
import Trigger_config from "./trigger_config.vue";
import Pre_conditions_config from "./pre_conditions_config.vue";
import Complete_conditions_config from "./complete_conditions_config.vue";

export default Vue.extend({

    name: 'action_config_wizard_base',
    components: {
      Complete_conditions_config,
      Pre_conditions_config,
      Trigger_config

    },
    props: ['action', 'project_string_id', 'actions_list', 'steps_config_prop'],

    mounted() {

    },

    data() {
      return {
        step: 1,
        loading_steps: false,
        is_open: true,
        search: '',
        default_steps_config: default_steps_config,
        error: null

      }
    },
    watch: {},
    computed: {
      steps_config: function () {
        if (this.steps_config_prop) {
          return this.steps_config_prop
        }
        return this.default_steps_config
      },
      visible_steps: function () {
        let res = {}
        for (let key of Object.keys(this.steps_config)) {
          let current = this.steps_config[key]
          if (!current.hide) {
            res[key] = current
          }
        }
        return res
      }
    },
    methods: {
      on_change_step: function(){

      },
      on_next_button_click: function(){
        if(this.step <= 0){
          return
        }
        this.step += 1
        this.$emit('next_step')
      },
      on_prev_button_click: function(){
        if(this.step <= Object.keys(this.steps_config).length)
        this.step -= 1
        this.$emit('previous_step')
      }
    }
  }
) </script>


<style>
code {
  width: 100%;
  height: 100% !important;
}
</style>
