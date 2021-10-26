<template>
  <v-container fluid>
    <div class="d-flex mb-8 justify-space-between">
      <h1 class="font-weight-medium text--primary mr-4">
        Add Guides to Your Task Template:
      </h1>
      <tooltip_button
        tooltip_message="Create UI Schema"
        @click="open_ui_schema_creation"
        button_color="primary"
        icon="mdi-plus"
        button_message="Upload Files"
        color="white">
      </tooltip_button>
    </div>

    <v_error_multiple :error="error"></v_error_multiple>
    <p class="text--primary">
      Guides are used to explain annotators the requirements for correctly annotating your files.
    </p>
    <p class="text--primary">
      Awards are badges that can tell you about an annotator skills. You can require them for certain
      tasks requiring more domain expertise.
    </p>

    <v-container fluid>
      <v_guide_list :job_id="job.id"
                    :project_string_id="project_string_id"
                    :mode=" 'attach' "
      >
      </v_guide_list>


      <v-btn @click="show_credentials=!show_credentials"
             color="primary"
             outlined
             class="pa-2"
      >
        Optional: Awards
      </v-btn>

      <v_credential_type_attach_to_job
        v-if="show_credentials==true"
        :job_id="job_id">
      </v_credential_type_attach_to_job>

      <v_task_bid_new v-if="
                            job.type == 'Normal' &&
                            job.share_type == 'market'
                            "
                      :job="job">
      </v_task_bid_new>

    </v-container>

    <v-container fluid class="mt-8 pa-0 d-flex justify-space-between" style="width: 100%">
      <v-btn x-large color="primary" @click="$emit('previous_step')">Previous</v-btn>
      <v-btn :disabled="job.attached_directories_dict.attached_directories_list.length === 0"
             x-large
             color="primary"
             @click="on_next_button_click">
        Next
      </v-btn>
    </v-container>
  </v-container>

</template>

<script lang="ts">

  import axios from 'axios';


  import Vue from "vue";

  export default Vue.extend({
      name: 'step_ui_schema_task_template',
      props: [
        'project_string_id',
        'job'
      ],

      components: {

      },

      data() {
        return {
          error: {},
          show_credentials: false,
        }
      },
      created() {

      },

      computed: {

      },
      methods: {
        on_next_button_click: function(){
          this.$emit('next_step');
        },
      }
    }
  ) </script>
