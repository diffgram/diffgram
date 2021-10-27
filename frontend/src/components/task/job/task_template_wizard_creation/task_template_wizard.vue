<template>
  <v-container fluid style="width: 100%">
    <v-stepper v-model="step" style="height: 100%;" @change="on_change_step">
      <v-stepper-header class="ma-0 pl-8 pr-8">
        <v-stepper-step
          :complete="step > 1"
          step="1"
          editable
        >
          Start
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step
          :complete="step > 2"
          step="2"
          editable
        >
          Labels
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step
          :complete="step > 3"
          step="3"
          editable
        >
          Users
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step
          :complete="step > 4"
          step="4"
          editable
        >
          Upload
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step
          :complete="step > 5"
          step="5"
          editable
        >
          Datasets
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step
          :complete="step > 6"
          editable
          step="6">
          UI Schema
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step
          :complete="step > 7"
          editable
          step="7">
          Guides
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step
          :complete="step > 8"
          editable
          step="8">
          Other Configs
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
        <v_error_multiple :error="error"></v_error_multiple>
        <v-stepper-content step="1" style="height: 100%">
          <step_name_task_template
            :project_string_id="project_string_id"
            :job="job"
            :loading_steps="loading"

            @next_step="go_to_step(2)"
          ></step_name_task_template>

        </v-stepper-content>
        <v-stepper-content step="2" style="height: 100%">
          <step_label_selection_task_template
            :project_string_id="project_string_id"
            :job="job"
            :loading_steps="loading"
            @previous_step="go_to_step(1)"
            @next_step="go_to_step(3)"
          ></step_label_selection_task_template>


        </v-stepper-content>
        <v-stepper-content step="3" style="height: 100%">
          <step_users_selection
            :project_string_id="project_string_id"
            :job="job"
            :mode="mode"
            :loading_steps="loading"
            @previous_step="go_to_step(2)"
            @next_step="go_to_step(4)"
          ></step_users_selection>
        </v-stepper-content>

        <v-stepper-content step="4">
          <step_upload_files_task_template
            :project_string_id="project_string_id"
            :job="job"
            :loading_steps="loading"
            @previous_step="go_to_step(3)"
            @next_step="go_to_step(5)"
          ></step_upload_files_task_template>
        </v-stepper-content>

        <v-stepper-content step="5">
          <step_attach_directories_task_template
            :project_string_id="project_string_id"
            :job="job"
            :loading_steps="loading"
            @previous_step="go_to_step(4)"
            @next_step="go_to_step(6)"
          ></step_attach_directories_task_template>
        </v-stepper-content>

        <v-stepper-content step="6">
          <step_ui_schema_task_template
            :project_string_id="project_string_id"
            :job="job"
            :loading_steps="loading"
            @previous_step="go_to_step(5)"
            @next_step="go_to_step(7)"
          ></step_ui_schema_task_template>
        </v-stepper-content>

        <v-stepper-content step="7">
          <step_guides_task_template
            :project_string_id="project_string_id"
            :job="job"
            :loading_steps="loading"
            @previous_step="go_to_step(6)"
            @next_step="go_to_step(8)"
          ></step_guides_task_template>
        </v-stepper-content>

        <v-stepper-content step="8">
          <step_advanced_options_task_template
            :project_string_id="project_string_id"
            :job="job"
            :loading_steps="loading"
            @previous_step="go_to_step(7)"
            @next_step="launch_task_template"
          ></step_advanced_options_task_template>
        </v-stepper-content>

      </v-stepper-items>

    </v-stepper>

  </v-container>

</template>

<script lang="ts">

  import axios from 'axios';
  import step_name_task_template from './step_name_task_template'
  import step_advanced_options_task_template from './step_advanced_options_task_template'
  import step_guides_task_template from './step_guides_task_template'
  import step_upload_files_task_template from './step_upload_files_task_template'
  import step_label_selection_task_template from './step_label_selection_task_template'
  import step_ui_schema_task_template from './step_ui_schema_task_template'
  import step_users_selection from './step_users_selection'
  import step_attach_directories_task_template from './step_attach_directories_task_template'


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
        'mode':{
          default: null
        }
      },

      components: {
        step_name_task_template,
        step_upload_files_task_template,
        step_guides_task_template,
        step_users_selection,
        step_ui_schema_task_template,
        step_advanced_options_task_template,
        step_label_selection_task_template,
        step_attach_directories_task_template
      },
      created: async function(){
        if(this.$props.job_id_route){
          await this.fetch_job_api();
        }
      },
      data() {
        return {
          step: 1,
          total_steps: 6,
          loading: false,
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
        job_update: async function () {
          this.loading = true
          const job = this.$props.job;
          this.error = {};
          try {
            const response = await axios.post(
              `/api/v1/project/${this.project_string_id}/job/update`,
              {
                ...job,
                job_id: job.id,
              }
            )
            // Handle job hash / draft / job status
            if (response.data.log.success == true) {
              this.loading = false
              this.$emit('job-updated', job)
              return response
            }

          } catch (error) {
            this.loading = false
            this.error = this.$route_api_errors(error)
            return false;
          }

        },
        launch_task_template: async function(){
          this.error = {}

          this.loading = true

          try {
            // const response_output_dirs = await this.add_output_actions_to_job();
            // if (!response_output_dirs) {
            //   return
            // }
            // const response_dirs_update = await this.add_dirs_to_job_api();
            // if (!response_dirs_update) {
            //   return
            // }
            const response = await axios.post(
              '/api/v1/job/launch',
              {
                job_id: this.job.id

              });
            // Push to success / stats page?
            // Show success?

            let launch_flow = response.data.log.info.launch_flow

            if (launch_flow == 'now') {
              this.$router.push('/job/' + this.job_id + '?success_launch=true')
            } else if (launch_flow == 'soon') {
              this.$router.push('/job/list?success_launch=true')

            }

          } catch (error) {
            console.error(error)
            this.error = this.$route_api_errors(error)
            console.log('errro', this.error)
            if(this.error.job_id){
              this.error.info = 'Please complete all the steps to launch the job.'
            }
          }
          finally{
            this.loading = false
          }
        },

        go_to_step: async function (step) {
          await this.job_update();
          this.step = step;
        },
        on_change_step: function () {

        },
      }
    }
  ) </script>
