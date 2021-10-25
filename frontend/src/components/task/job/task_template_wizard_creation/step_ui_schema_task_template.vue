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


    <v-container fluid class="mt-8 pa-0 d-flex justify-space-between" style="width: 100%">
      <v-btn x-large color="primary" @click="$emit('previous_step')">Previous</v-btn>
      <v-btn :disabled="job.attached_directories_dict.attached_directories_list.length === 0" x-large color="primary" @click="on_next_button_click">Next</v-btn>
    </v-container>
  </v-container>

</template>

<script lang="ts">

  import axios from 'axios';
  import upload_wizard_sheet from '../../../input/upload_wizard_sheet'
  import job_file_routing from '../job_file_routing'
  import job_pipeline_mxgraph from '../job_pipeline_mxgraph'

  import Vue from "vue";

  export default Vue.extend({
      name: 'step_ui_schema_task_template',
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
        verify_labels: function(){
          if(!this.$props.job.label_file_list || this.$props.job.label_file_list.length === 0){
            this.error = {
              name: 'At least 1 user should be assigned to the task template.'
            }
            return false
          }
          return true
        },
        on_next_button_click: function(){
          this.error = {};
          let labels_ok = this.verify_labels();
          if(labels_ok){
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
