<template>
  <v-container fluid data-cy="task-template-step-name">
    <h1 data-cy="wizard-title" class="font-weight-medium text--primary mb-8">
      <v-icon color="primary" class="mr-4" size="48">mdi-brush</v-icon>
      {{ title }}
    </h1>
    <v_error_multiple :error="error"></v_error_multiple>
    <p class="text--primary" data-cy="wizard-name-subtitle">
      {{ message }}
    </p>

    <v-text-field label="Name"
                  data-cy="task-template-name-input"
                  v-model="job.name">
    </v-text-field>

    <wizard_navigation
      @next="on_next_button_click"
      :loading_next="loading"
      :disabled_next="loading"
      :skip_visible="false"
      :back_visible="false"
    >

    </wizard_navigation>
  </v-container>

</template>

<script lang="ts">

import axios from '../../../../services/customAxiosInstance';

import Vue from "vue";

export default Vue.extend({
    name: 'step_name_task_template',
    props: [
      'project_string_id',
      'job',
      'title',
      'message'
    ],

    components: {},

    data() {
      return {
        error: {},
        loading: false,
      }
    },
    created() {

    },

    computed: {},
    methods: {
      verify_name: function () {
        if (!this.$props.job.name || this.$props.job.name === '') {
          this.error = {
            name: 'Name must not be empty.'
          }
          return false
        }
        return true
      },
      on_next_button_click: async function () {
        this.error = {};
        let name_ok = this.verify_name();
        if (name_ok) {
          await this.job_new();
          this.$emit('next_step');
        }
      },
      job_new: async function () {
        if (this.job.id != undefined) {
          return
        }
        this.loading = true
        this.job_new_error = {}
        let job = {...this.$props.job};
        // QUESTION
        // Not clear if we want to do this as a computed property or...

        // careful to update with share property that's seperate due to dict thing.
        const url = `/api/v1/project/${this.project_string_id}/job/new`

        try {
          const response = await axios.post(url, job)
          // Handle job hash / draft / job status
          if (response.data.log.success == true) {
            this.job.id = response.data.job.id;
            this.loading = false
            this.success_action = 'Job created successfully.'
            return response
          }

        } catch (error) {
          console.error(error);
          this.loading = false
          this.error = this.$route_api_errors(error)
          return error;
        }
      },

    }
  }
) </script>
