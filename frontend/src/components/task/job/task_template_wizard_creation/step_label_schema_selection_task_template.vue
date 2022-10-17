<template>
  <v-container fluid data-cy="task-template-labels-step">
    <div class="d-flex mb-8 justify-space-between">
      <h1 data-cy="step-labels-title" class="font-weight-medium text--primary mr-4">
        What Label Schema Do you Want to Use?
      </h1>
      <standard_button
        data-cy="manage-labels-button"
        tooltip_message="Quick Edit Project Level Schema"
        @click="open_labels_dialog"
        button_color="primary"
        icon="mdi-format-paint"
        button_message="Manage Schema"
        color="white">
      </standard_button>
    </div>

    <v_error_multiple :error="error"></v_error_multiple>
    <p class="text--primary">
      Select The Schema you want to use:
    </p>
    <label_schema_selector
      :initial_schema="job.label_schema"
      :project_string_id="project_string_id"
      ref="label_select"
      @change="on_change_schema"

    >
    </label_schema_selector>

    <wizard_navigation
      @next="on_next_button_click"
      :loading_next="loading_steps"
      :disabled_next="loading_steps"
      @back="$emit('previous_step')"
      :skip_visible="false"
    >
    </wizard_navigation>
    <label_manager_dialog
                          v-if="job.label_schema"
                          :schema="job.label_schema"
                          :project_string_id="project_string_id"
                          ref="label_manager_dialog">

    </label_manager_dialog>

  </v-container>

</template>

<script lang="ts">
  import label_select_only from '../../../label/label_select_only'
  import label_schema_selector from '../../../label/label_schema_selector'
  import label_manager_dialog from '../../../label/label_manager_dialog'

  import Vue from "vue";

  export default Vue.extend({
      name: 'step_label_schema_task_template',
      props: [
        'project_string_id',
        'job',
        'loading_steps',
      ],

      components: {
        label_select_only,
        label_manager_dialog,
        label_schema_selector
      },

      data() {
        return {
          error: {},
          request_refresh_labels: new Date(),
        }
      },
      created() {

      },

      computed: {

      },
      methods: {
        verify_labels_schema: function(){
          if(!this.$props.job.label_schema_id){
            this.error = {
              name: 'At least 1 label should be assigned to the task template.'
            }
            return false
          }
          return true
        },
        on_next_button_click: function(){
          this.error = {};
          let labels_ok = this.verify_labels_schema();
          if(labels_ok){
            this.$emit('next_step');
          }
        },
        on_change_schema: function(schema){
          this.job.label_schema_id = schema.id;
          this.job.label_schema = schema;
        },
        on_label_created: function(){
          this.$refs.label_select.refresh_label_list_from_project();
        },
        open_labels_dialog: function () {
          this.$refs.label_manager_dialog.open()
        },
      }
    }
  ) </script>
