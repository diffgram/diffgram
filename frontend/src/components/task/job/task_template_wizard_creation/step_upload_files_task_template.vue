<template>
  <v-container fluid data-cy="task-template-upload-step">
    <div class="d-flex mb-8 justify-space-between">
      <h1 class="font-weight-medium text--primary mr-4">
        Do you have fresh data to upload?
      </h1>

    </div>

    <v_error_multiple :error="error"></v_error_multiple>
    <p class="text--primary">
      Upload Files To Your Datasets (Optional)
    </p>

    <v-row class="d-flex justify-center align-center" style="min-height: 500px">
      <tooltip_button
        :x-large="true"
        tooltip_message="Upload File"
        @click="open_upload_wizard"
        button_color="success"
        data-cy="upload_button"
        icon="mdi-upload"
        button_message="Upload Files"
        color="white">
      </tooltip_button>
    </v-row>


    <wizard_navigation
      @next="on_next_button_click"
      :loading_next="loading_steps"
      :disabled_next="loading_steps"
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
        'job',
        'loading_steps'
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
        on_next_button_click: function(){
          this.error = {};
          this.$emit('next_step');
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
