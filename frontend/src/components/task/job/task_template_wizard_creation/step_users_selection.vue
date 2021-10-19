<template>
  <v-container fluid>
    <div class="d-flex mb-8 justify-space-between">
      <h1 class="font-weight-medium text--primary mr-4">
        Select Users
      </h1>
    </div>

    <v_error_multiple :error="error"></v_error_multiple>
    <p class="text--primary">
      Select The Users assigned to the the task template. This users will be able to see and annotate
      the tasks inside this task template.
    </p>


    <h4>Select Users: </h4>
    <member_select
      v-model="job.member_list_ids"
      label="Select Specific Users"
      :member_list="$store.state.project.current.member_list"
      :multiple="true"
      :initial_value="job.id != undefined ? job.member_list_ids : ['all']"
      :allow_all_option="true"
    >
    </member_select>


    <v-container fluid class="mt-8 pa-0 d-flex justify-space-between" style="width: 100%">
      <v-btn x-large color="primary" @click="$emit('previous_step')">Previous</v-btn>
      <v-btn x-large color="primary" @click="on_next_button_click">Next</v-btn>
    </v-container>

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
        'job'
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
        verify_members: function(){
          if(!this.$props.job.member_list_ids || this.$props.job.member_list_ids.length === 0){
            this.error = {
              name: 'At least 1 user should be assigned.'
            }
            return false
          }
          return true
        },
        on_next_button_click: function(){
          this.error = {};
          let memers_ok = this.verify_members();
          if(memers_ok){
            this.$emit('next_step');
          }
        },
      }
    }
  ) </script>
