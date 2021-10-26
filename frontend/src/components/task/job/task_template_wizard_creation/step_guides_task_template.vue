<template>
  <v-container fluid>
    <div class="d-flex mb-8 justify-space-between">
      <h1 class="font-weight-medium text--primary mr-4">
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
      <h2 class="ma-0">Set Your Guide (Optional): </h2>
      <guide_selector
        :project_string_id="project_string_id"
        @change="on_change_guide"
      >

      </guide_selector>
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
  import guide_selector from '../../guide/guide_selector'

  import Vue from "vue";

  export default Vue.extend({
      name: 'step_guides_task_template',
      props: [
        'project_string_id',
        'job'
      ],

      components: {
        guide_selector
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
        on_change_guide: function(guide){
          this.job.guide = guide;
        },
        on_next_button_click: function () {
          this.$emit('next_step');
        },
        open_guides: function(){
          let routeData = this.$router.resolve({
            path: `/project/${this.project_string_id}/guide/list`,
            query: {edit_schema: true}
          });
          window.open(routeData.href, '_blank');
        }
      }
    }
  ) </script>
