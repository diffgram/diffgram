<template>
  <v-container fluid>
    <div class="d-flex mb-8 justify-space-between">
      <h1 class="font-weight-medium text--primary mr-4">
        Select UI Schema:
      </h1>
      <tooltip_button
        tooltip_message="Manage UI Schema"
        @click="open_ui_schema_creation"
        button_color="primary"
        icon="mdi-cog"
        button_message=" Manage UI Schemas"
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
        :show_default_option="true"
        @change="on_change_schema">

      </ui_schema_selector>

    </v-container>

    <wizard_navigation
      @next="on_next_button_click"
      :loading_next="loading_steps"
      @back="$emit('previous_step')"
      :skip_visible="false"
    >
    </wizard_navigation>
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
        'job',
        'loading_steps',
      ],

      components: {
        job_file_routing,
        job_pipeline_mxgraph,
        ui_schema_selector,
      },

      data() {
        return {
          error: {},
          open_wizard: false,
        }
      },
      created() {

      },

      computed: {},
      methods: {
        on_change_schema: function (ui_schema) {
          this.job.ui_schema_id = ui_schema.id;
        },
        on_next_button_click: function () {
          this.$emit('next_step');
        },
        open_ui_schema_creation: function () {
          let routeData = this.$router.resolve({
            path: `/studio/annotate/${this.project_string_id}`,
            query: {edit_schema: true}
          });
          window.open(routeData.href, '_blank');
        },
      }
    }
  ) </script>
