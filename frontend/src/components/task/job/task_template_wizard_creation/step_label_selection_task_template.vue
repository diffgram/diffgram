<template>
  <v-container fluid data-cy="task-template-labels-step">
    <div class="d-flex mb-8 justify-space-between">
      <h1 data-cy="step-labels-title" class="font-weight-medium text--primary mr-4">
        What labels should be visible?
      </h1>
      <tooltip_button
        data-cy="manage-labels-button"
        tooltip_message="Quick Edit Project Level Schema"
        @click="open_labels_dialog"
        button_color="primary"
        icon="mdi-format-paint"
        button_message="Manage Labels & Attributes"
        color="white">
      </tooltip_button>
    </div>

    <v_error_multiple :error="error"></v_error_multiple>
    <p class="text--primary">
      Select The Labels to Use on This Task Template. All are selected by default.
    </p>
    <label_select_only
      :project_string_id="project_string_id"
      label_prompt="Schema Selected For Tasks"
      :mode=" 'multiple' "
      datacy="label-select"
      @label_file="on_change_label_file($event)"
      :load_selected_id_list="job.label_file_list"
      :select_all_at_load="true"
      ref="label_select"

    >
    </label_select_only>

    <wizard_navigation
      @next="on_next_button_click"
      :loading_next="loading_steps"
      :disabled_next="loading_steps"
      @back="$emit('previous_step')"
      :skip_visible="false"
    >
    </wizard_navigation>

    <label_manager_dialog @label_created="on_label_created"
                          :project_string_id="project_string_id"
                          ref="label_manager_dialog">

    </label_manager_dialog>
  </v-container>

</template>

<script lang="ts">

  import axios from 'axios';
  import label_select_only from '../../../label/label_select_only'
  import label_manager_dialog from '../../../label/label_manager_dialog'

  import Vue from "vue";

  export default Vue.extend({
      name: 'step_label_task_template',
      props: [
        'project_string_id',
        'job',
        'loading_steps',
      ],

      components: {
        label_select_only,
        label_manager_dialog
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
        on_change_label_file: function(label_file_list){
          this.job.label_file_list = label_file_list;
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
