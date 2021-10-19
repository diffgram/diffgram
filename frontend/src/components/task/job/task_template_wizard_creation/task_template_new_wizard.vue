<template>
  <v-container fluid style="width: 100%">
    <v-stepper v-model="step" style="height: 100%;" @change="on_change_step">
      <v-stepper-header class="ma-0 pl-8 pr-8">
        <v-stepper-step
          :complete="step > 1"
          step="1"
        >
          Start
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step
          :complete="step > 2"
          step="2"
        >
          Label Selection & Configurations
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step
          :complete="step > 3"
          step="3"
        >
          Assign Users
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step
          :complete="step > 4"
          step="4">
          Dataset Binding
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step
          :complete="step > 5"
          step="5">
          Guides & Awards
        </v-stepper-step>
        <v-divider></v-divider>
      </v-stepper-header>

      <v-progress-linear
        color="secondary"
        striped
        v-model="global_progress"
        height="12"
      >
      </v-progress-linear>

      <v-stepper-items style="height: 100%">
        <v-stepper-content step="1" style="height: 100%">
          <step_name_task_template
            :project_string_id="project_string_id"
            :job="job"
            @next_step="go_to_step(2)"
          ></step_name_task_template>

        </v-stepper-content>
        <v-stepper-content step="2" style="height: 100%">
          <step_label_selection_task_template
            :project_string_id="project_string_id"
            :job="job"
            @next_step="go_to_step(3)"
          ></step_label_selection_task_template>
        </v-stepper-content>
        <v-stepper-content step="3" style="height: 100%">

        </v-stepper-content>

        <v-stepper-content step="4">

        </v-stepper-content>

        <v-stepper-content step="5">

        </v-stepper-content>

        <v-stepper-content step="6">

        </v-stepper-content>

      </v-stepper-items>

    </v-stepper>

  </v-container>

</template>

<script lang="ts">

  import axios from 'axios';
  import step_name_task_template from './step_name_task_template'
  import step_label_selection_task_template from './step_label_selection_task_template'


  import Vue from "vue";

  export default Vue.extend({
      name: 'task_template_new_wizard',
      props: {
        'project_string_id': {
          default: null
        },
        'job': {
          default: null
        },
        'job_id_route': {
          default: null
        },
      },

      components: {
        step_name_task_template,
        step_label_selection_task_template
      },

      data() {
        return {
          step: 1,
          total_steps: 4,
          error: {},

        }
      },
      computed: {
        global_progress: function () {
          return (this.step * 100) / this.total_steps;
        },
        bread_crumb_list: function () {
          return [
            {
              text: 'Tasks',
              disabled: false,
              to: '/job/list'
            },
            {
              text: 'New Template',
              disabled: true
            }
          ]
        }
      },
      methods: {
        go_to_step: function (step) {
          this.step = step;
        },
        on_change_step: function () {

        },
      }
    }
  ) </script>
