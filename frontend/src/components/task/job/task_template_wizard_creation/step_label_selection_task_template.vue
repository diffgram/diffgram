<template>
  <v-container fluid>
    <h1 class="font-weight-medium text--primary mb-8">Select Labels</h1>
    <v_error_multiple :error="error"></v_error_multiple>
    <p class="text--primary">
      Select The Labels to Use on This Task Template. All are selected by default.
    </p>
    <div class="pr-4">
      <tooltip_button
        tooltip_message="Quick Edit Project Level Schema"
        @click="open_labels_dialog"
        icon="mdi-format-paint"
        :icon_style="true"
        :large="true"
        color="primary">
      </tooltip_button>
    </div>

    <h4>Select Labels: </h4>
    <label_select_only
      :project_string_id="project_string_id"
      label_prompt="Schema Selected For Tasks"
      :mode=" 'multiple' "
      data-cy="label-select"
      @label_file="on_change_label_file($event)"
      :load_selected_id_list="job.label_file_list"
      :select_all_at_load="true"
      ref="label_select"

    >
    </label_select_only>


    <v-container fluid class="mt-8 pa-0 d-flex justify-end" style="width: 100%">
<!--      <v-btn x-large color="primary" @click="$emit('previous_step')">Previous</v-btn>-->
      <v-btn x-large color="primary" @click="on_next_button_click">Next</v-btn>
    </v-container>

    <label_manager_dialog @label_created="on_label_created"
                          :project_string_id="project_string_id"
                          ref="label_manager_dialog">

    </label_manager_dialog>
  </v-container>

</template>

<script lang="ts">

  import axios from 'axios';
  import label_select_only from '../../../label/label_select_only'

  import Vue from "vue";

  export default Vue.extend({
      name: 'step_name_task_template',
      props: [
        'project_string_id',
        'job'
      ],

      components: {
        label_select_only
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
          if(!this.$props.job.label_file_list || this.$props.job.label_file_list.lengh === 0){
            this.error = {
              name: 'Labels must not be empty.'
            }
            return false
          }
          return true
        },
        on_next_button_click: function(){
          this.error = {};
          let name_ok = this.verify_labels();
          if(name_ok){
            this.$emit('next_step');
          }
        },
        on_change_label_file: function(){

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
