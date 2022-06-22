<template>
  <v-stepper v-model="step"
             style="height: 100%"
             @change="on_change_step"
             class="elevation-0"
             >
    <v-stepper-items style="height: 80%">
      <v_error_multiple :error="error"></v_error_multiple>

      <v-stepper-content
        v-for="(keyStep, index) in Object.keys(steps_config)"
        :step="steps_config[keyStep].number">
        <slot :name="keyStep" v-if="keyStep === 'action_config'">

        </slot>
        <slot :name="keyStep" v-if="keyStep === 'triggers'" >
          <trigger_config :project_string_id="project_string_id"
                          :actions_list=actions_list
                          :action_template="action_template"
                          :action="action">

          </trigger_config>
        </slot>
        <slot :name="keyStep" v-if="keyStep === 'pre_conditions'">
          <pre_conditions_config
            :action_template="action_template"
            :project_string_id="project_string_id"
            :actions_list=actions_list
            :action="action">

          </pre_conditions_config>
        </slot>
        <slot :name="keyStep" v-if="keyStep === 'completion_trigger'">
          <complete_conditions_config
            :project_string_id="project_string_id"
            :action_template="action_template"
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
      <v-stepper-content :step="Object.keys(steps_config).length + 1">
        <slot name="sucess_config">
          <v-container class="d-flex flex-column justify-center align-center">
            <v-icon color="success" size="256">mdi-check</v-icon>
            <h1>Action Configured Sucessfully.</h1>
            <v-btn color="success" @click="open_action_selector"><v-icon>mdi-plus</v-icon>Add Another Action</v-btn>
          </v-container>
          <wizard_navigation
            @next="on_next_button_click"
            :next_visible="false"
            :loading_next="loading_steps"
            :disabled_next="loading_steps"
            :disabled_back="step <= 1"
            @back="on_prev_button_click"
            :skip_visible="false">

          </wizard_navigation>
        </slot>
      </v-stepper-content>

    </v-stepper-items>


    <v-stepper-header class="ma-0 pl-8 pr-8 " style="height: 20%">
      <template v-for="(key, index) in Object.keys(steps_config)">
        <v-stepper-step
          :complete="step > steps_config[key].number"
          :step="steps_config[key].number"
          editable
        >
          {{ steps_config[key].header_title }}
        </v-stepper-step>
        <v-divider v-if="index < Object.keys(steps_config).length - 1"></v-divider>
      </template>
    </v-stepper-header>
  </v-stepper>
</template>

<script lang="ts">
import Vue from "vue";
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
    props: [
      'action', 
      'project_string_id', 
      'actions_list', 
      'steps_config', 
      'action_template'
    ],
    data() {
      return {
        step: 1,
        loading_steps: false,
        is_open: true,
        search: '',
        error: null
      }
    },
    methods: {
      open_action_selector: function(){
        this.$emit('open_action_selector')
      },
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
        console.log('Object.keys(this.steps_config).length', Object.keys(this.steps_config).length, this.step)
        if(this.step <= 1){
          return
        }
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
