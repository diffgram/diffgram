<template>
  <div id="input_view" style="min-height: 600px" class="d-flex flex-column align-center justify-center">
    <h1 class="font-weight-medium text--primary mb-2">Upload Files</h1>
    <h3>
      Add Some files to your project, click the button below to
      start the upload wizard.
    </h3>
    <v-btn
      class="mt-8"
      @click="open_upload_wizard_sheet"
      data-cy="start_upload_wizard"
      color="success"
      x-large>
      <v-icon>mdi-upload</v-icon>
      Start New Data Upload
    </v-btn>
    <upload_wizard_sheet
      v-if="open_wizard"
      :project_string_id="project_string_id"
      @closed="on_wizard_closed"
      @upload_success="on_upload_success"
      ref="upload_wizard_sheet">

    </upload_wizard_sheet>

  </div>
</template>

<script lang="ts">

  import Vue from "vue";
  import upload_wizard_sheet from '../input/upload_wizard_sheet';

  export default Vue.extend({
      name: 'upload_step_wizard',
      components: {
        upload_wizard_sheet
      },
      props: {
        'project_string_id': {
          default: null
        },
      },

      data() {

        return {
          open_wizard: false

        }

      },
      computed: {},
      watch: {},
      mounted() {


      },
      methods: {
        on_wizard_closed: function () {

        },
        on_upload_success: function () {
          this.$emit('upload_success')
        },
        open_upload_wizard_sheet: async function () {
          this.open_wizard = true;
          await this.$nextTick();
          this.$refs.upload_wizard_sheet.open();
        }
      }
    }
  ) </script>

