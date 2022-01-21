<template>
  <v-container fluid data-cy="task-template-guide-step">
    <div class="d-flex mb-8 justify-space-between">
      <h1 data-cy="task-template-guide-step-title" class="font-weight-medium text--primary mr-4">
        Guides Setup:
      </h1>
      <tooltip_button
        tooltip_message="Create Guides"
        @click="open_guides"
        button_color="primary"
        icon="mdi-plus"
        button_message="Create Guides"
        color="white">
      </tooltip_button>
    </div>

    <v_error_multiple :error="error"></v_error_multiple>
    <p class="text--primary">
      Guides are used to explain annotators the requirements for correctly annotating your files.
      This is an optional step.
    </p>


    <v-container fluid>
      <h2 class="ma-0" data-cy="task-template-guide-step-subtitle">Set Your Guide (Optional): </h2>
      <guide_selector
        data-cy="guide-selector"
        :project_string_id="project_string_id"
        @change="on_change_guide"
        ref="guide_selector"
      >

      </guide_selector>
    </v-container>

    <wizard_navigation
      @next="on_next_button_click"
      :disabled_next="loading"
      :loading_next="loading_steps"
      @back="$emit('previous_step')"
      :skip_visible="false"
    >
    </wizard_navigation>

    <v-dialog v-model="dialog_open"
              :close-on-content-click="false"
              :nudge-width="200"
              offset-x>


      <v_guide_new_or_edit
        :project_string_id="project_string_id"
        :mode="'new'"
        @guide_new_success="on_guide_created">
      </v_guide_new_or_edit>

    </v-dialog>
  </v-container>

</template>

<script lang="ts">

  import axios from 'axios';
  import guide_selector from '../../guide/guide_selector'

  import Vue from "vue";

  export default Vue.extend({
      name: 'step_guides_task_template',
      props: [
        'project_string_id',
        'job',
        'loading_steps'
      ],

      components: {
        guide_selector
      },

      data() {
        return {
          error: {},
          show_credentials: false,
          dialog_open: false,
          loading: false,
        }
      },
      created() {

      },

      methods: {
        on_change_guide: function (guide) {
          this.job.guide = guide;
          this.attach_selected(guide.id, 'default', 'update')
        },
        on_next_button_click: function () {
          this.$emit('next_step');
        },
        open_guides: function () {
          this.dialog_open = true;
        },
        on_guide_created: function (guide) {
          this.$refs.guide_selector.guide_list_api();
        },
        attach_selected: async function (guide_id, attach_kind, update_or_remove) {


          this.loading = true
          this.show_success_attach = false
          this.error = {}
          try {
            const response = await axios.post('/api/v1/guide/attach/job',
              {
                'update_or_remove': update_or_remove,
                'kind': attach_kind,
                'job_id': this.job.id,
                'guide_id': guide_id

              })

          } catch (e) {
            this.error = e.response.data.log.error
            console.error(e)
            this.loading = false
          }

        },
      }
    }
  ) </script>
