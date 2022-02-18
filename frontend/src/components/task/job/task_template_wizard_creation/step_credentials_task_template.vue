<template>
  <v-container fluid data-cy="task-template-credentials-step" v-if="job">
    <div class="d-flex flex-column mb-8 justify-space-between">
      <div class="d-flex flex-column">
        <h2 class="font-weight-medium text--primary mr-4" data-cy="credentials-step-title">
          Credentials:
        </h2>
        <p>Select the credentials and click Require/Award in order to require or award them.</p>
        <p><strong class="font-weight-bold">Note:</strong> Awards only available for exams.</p>
        <v_credential_type_attach_to_job :job_id="job.id" :allow_awards="job.type === 'exam_template'">
        </v_credential_type_attach_to_job>
      </div>


    </div>

    <v_error_multiple :error="error"></v_error_multiple>



  <wizard_navigation
    @next="on_next_button_click"
    :next_visible="false"
    :loading_next="loading_steps"
    :disabled_next="loading_steps"
    @back="$emit('previous_step')"
    :skip_visible="false">

    <template slot="next">
      <v-btn
        x-large
        @click="on_next_button_click"
        color="success"
        data-cy="wizard_navigation_next"
        :disabled="loading_steps"
        :loading="loading_steps"
      >
        <v-icon left>mdi-rocket-launch</v-icon>
        Launch Task Template
      </v-btn>
    </template>

  </wizard_navigation>
  </v-container>

</template>

<script lang="ts">

import guide_selector from '../../guide/guide_selector'
import userscript_select from '../../../annotation/userscript/userscript_select'

import Vue from "vue";

export default Vue.extend({
    name: 'step_credentials_task_template',
    props: [
      'project_string_id',
      'job',
      'loading_steps',
    ],

    components: {
      guide_selector,
      userscript_select,
    },

    data() {
      return {
        error: {},
        show_credentials: false,
        loading: false,
        type_list: [
          {
            display_name: 'Normal',
            value: 'Normal'
          },
          {
            display_name: 'Exam',
            value: 'exam_template'
          }
        ],
        share_list: [],
        file_handling_list: [
          {
            'display_name': 'Use Existing (Default)',
            'name': 'use_existing',
            'icon': 'mdi-cached',
            'color': 'primary'
          },
          {
            'display_name': 'Isolate (New Versions of Files)',
            'name': 'isolate',
            'icon': 'mdi-ab-testing',
            'color': 'primary'
          }
        ],
      }
    },
    created() {

    },

    methods: {
      on_next_button_click: function () {
        this.$emit('next_step');
      }
    }
  }
) </script>
