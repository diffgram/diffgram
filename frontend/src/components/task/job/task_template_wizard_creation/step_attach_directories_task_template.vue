<template>
  <v-container fluid>
    <div class="d-flex mb-8 justify-space-between">
      <h1 class="font-weight-medium text--primary mr-4">
        Attach Directories
      </h1>
      <tooltip_button
        tooltip_message="Upload File"
        @click="open_upload_wizard"
        button_color="primary"
        icon="mdi-upload"
        button_message="Upload Files"
        color="white">
      </tooltip_button>
    </div>

    <v_error_multiple :error="error"></v_error_multiple>
    <p class="text--primary">
      Select The Datasets to attach to your task template
    </p>

    <v-row class="d-flex justify-space-between">
      <v-col cols="6">
        <job_file_routing
          :job="job"
          style="border-right: 2px solid #e6e6e6"
          :latest_dataset="latest_dataset"
          :project_string_id="project_string_id"
          ref="job_file_routing"
          @directories_updated="on_attached_dirs_updated"
          @output_dir_actions_update="on_output_dirs_updated"
        ></job_file_routing>

      </v-col>
      <v-col cols="6">
        <job_pipeline_mxgraph ref="job_pipepline" :job_object="job"></job_pipeline_mxgraph>
      </v-col>
    </v-row>

    <wizard_navigation
      @next="on_next_button_click"
      :disabled_next="job.attached_directories_dict.attached_directories_list.length === 0"
      @back="$emit('previous_step')"
      :skip_visible="false"
    >
    </wizard_navigation>

    <upload_wizard_sheet
      v-if="open_wizard"
      :project_string_id="project_string_id"
      :initial_dataset="latest_dataset"
      ref="upload_wizard_sheet"
      @closed="on_close_wizard"
    >

    </upload_wizard_sheet>
  </v-container>

</template>

<script lang="ts">

  import axios from 'axios';
  import upload_wizard_sheet from '../../../input/upload_wizard_sheet'
  import job_file_routing from '../job_file_routing'
  import job_pipeline_mxgraph from '../job_pipeline_mxgraph'

  import Vue from "vue";

  export default Vue.extend({
      name: 'step_attach_directories_task_template',
      props: [
        'project_string_id',
        'job'
      ],

      components: {
        job_file_routing,
        upload_wizard_sheet,
        job_pipeline_mxgraph,
      },

      data() {
        return {
          error: {},
          latest_dataset: undefined,
          output_dir: {},
          open_wizard: false,
          request_refresh_labels: new Date(),
        }
      },
      created() {

      },

      computed: {

      },
      methods: {
        async add_output_actions_to_job() {
          this.loading = true
          this.show_success = false
          this.error_launch = {}
          if (this.output_dir.action === 'copy' || this.output_dir.action === 'move') {
            if (!this.output_dir.directory) {
              this.error_launch = {
                output_dir: 'Please select a directory for copy/move after tasks are completed.'
              }
              this.loading = false;
              return false
            }
          }
          try {
            const response = await axios.post(
              '/api/v1/project/' + this.project_string_id
              + '/job/set-output-dir',
              {
                output_dir: this.output_dir.directory ? this.output_dir.directory.directory_id.toString() : undefined,
                output_dir_action: this.output_dir.action,
                job_id: parseInt(this.job.id),
              })
            return response
          } catch (error) {
            if (error.response) {
              this.error = error.response.data.log.error
            }
            this.loading = false
            return false
          }
        },
        async add_dirs_to_job_api() {
          this.loading = true
          this.show_success = false
          this.error_launch = {}
          let dir_list = [];
          if (this.job && this.job.attached_directories_dict && this.job.attached_directories_dict.attached_directories_list) {
            dir_list = this.job.attached_directories_dict.attached_directories_list
          }
          try {
            const response = await axios.post(
              '/api/v1/project/' + this.project_string_id
              + '/job/dir/attach',
              {
                directory_list: dir_list,
                job_id: parseInt(this.job.id),
              })
            return response
          } catch (error) {
            if (error.response) {
              this.error_launch = error.response.data.log.error
            }
            this.loading = false
            return false;
          }
        },
        verify_labels: function(){
          if(!this.$props.job.label_file_list || this.$props.job.label_file_list.length === 0){
            this.error = {
              name: 'At least 1 user should be assigned to the task template.'
            }
            return false
          }
          return true
        },
        on_next_button_click: async function(){
          this.error = {};
          let dirs_ok = await this.add_dirs_to_job_api();
          let out_dirs_ok = await this.add_output_actions_to_job();
          if(dirs_ok && out_dirs_ok){
            this.$emit('next_step');
          }
        },
        on_attached_dirs_updated: function(attached_dirs){
          this.latest_dataset = attached_dirs[attached_dirs.length - 1];
          this.job.attached_directories_dict = {
            attached_directories_list: attached_dirs.map(elm => elm)
          }
        },
        on_output_dirs_updated: async function(output_dir){
          this.output_dir = output_dir;
          if(!this.$refs.job_pipeline){
            return
          }
          await this.$refs.job_pipepline.get_directory()
          this.$refs.job_pipepline.redraw()
        },
        open_upload_wizard: async function(){
          this.open_wizard = true;
          await this.$nextTick();
          this.$refs.upload_wizard_sheet.open();
        },
        on_close_wizard: function(){

        }
      }
    }
  ) </script>
