<template>
  <v-container fluid>
    <div class="d-flex mb-8 justify-space-between">
      <h1 class="font-weight-medium text--primary mr-4">
        Awards Setup:
      </h1>
      <tooltip_button
        tooltip_message="Create Awards"
        @click="open_awards"
        button_color="primary"
        icon="mdi-plus"
        button_message="Create Awards"
        color="white">
      </tooltip_button>
    </div>

    <v_error_multiple :error="error"></v_error_multiple>
    <p class="text--primary">
      Awards are badges that can tell you about an annotator skills. You can require them for certain
      tasks requiring more domain expertise.
    </p>

    <v-container fluid>
      <h2 class="ma-0">Set Awards (Optional): </h2>

      <credential_type_attach_to_job
        :job="job"
        :job_id="job.id">
      </credential_type_attach_to_job>
    </v-container>

    <v-container fluid class="mt-8 pa-0 d-flex justify-space-between" style="width: 100%">
      <v-btn x-large color="primary" @click="$emit('previous_step')">Previous</v-btn>
      <v-btn x-large
             color="primary"
             @click="on_next_button_click">
        Next
      </v-btn>
    </v-container>
  </v-container>

</template>

<script lang="ts">

  import axios from 'axios';
  import credential_type_attach_to_job from '../../credential/credential_type_attach_to_job'

  import Vue from "vue";

  export default Vue.extend({
      name: 'step_awards_task_template',
      props: [
        'project_string_id',
        'job'
      ],

      components: {
        credential_type_attach_to_job
      },

      data() {
        return {
          error: {},
          show_credentials: false,
        }
      },
      created() {

      },

      methods: {
        on_next_button_click: function () {
          this.$emit('next_step');
        },
        open_awards: function(){
          let routeData = this.$router.resolve({
            path: `/project/${this.project_string_id}/guide/list`,
            query: {edit_schema: true}
          });
          window.open(routeData.href, '_blank');
        }
      }
    }
  ) </script>
