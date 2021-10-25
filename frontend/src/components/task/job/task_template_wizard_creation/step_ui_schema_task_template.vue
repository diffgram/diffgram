<template>
  <v-container fluid>
    <div class="d-flex mb-8 justify-space-between">
      <h1 class="font-weight-medium text--primary mr-4">
        Select UI Schema
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
      UI Schemas are a way to Customize the Annotation UI. You can show/hide buttons and configure
      what you want the annotators to see.
    </p>

    <v-container fluid>
      <ui_schema_selector
        :project_string_id="project_string_id"
        @change="on_change_schema">

      </ui_schema_selector>

    </v-container>

    <v-container fluid class="mt-8 pa-0 d-flex justify-space-between" style="width: 100%">
      <v-btn x-large color="primary" @click="$emit('previous_step')">Previous</v-btn>
      <v-btn :disabled="job.attached_directories_dict.attached_directories_list.length === 0" x-large color="primary" @click="on_next_button_click">Next</v-btn>
    </v-container>
  </v-container>

</template>

<script lang="ts">

  import axios from 'axios';
  import ui_schema_selector from '../../../ui_schema/ui_schema_selector'
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
        job_pipeline_mxgraph,
        ui_schema_selector,
      },

      data() {
        return {
          error: {},
          loading_schemas: false,
          ui_schema_list: [
            {
              label: 'Default Diffgram UI',
              value: undefined
            }
          ],
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
        on_change_schema: function(){

        }
      }
    }
  ) </script>
