<template>
  <div v-cloak>

    <v-dialog v-model="is_open" max-width="1500px" id="export-dialog">
      <v-card elevation="0">
        <v_upload_large :initial_dataset="latest_dataset" :show_labels_button="false":project_string_id="project_string_id" class="pa-8"></v_upload_large>

      </v-card>
    </v-dialog>

  </div>
</template>

<script lang="ts">

  import labels_view from '../../components/annotation/labels_view'
  import v_upload_large from '../upload_large'
  import Vue from "vue";

  export default Vue.extend({

      name: 'import_data_dialog',
      components: {
        labels_view: labels_view,
        v_upload_large: v_upload_large
      },
      props: ['project_string_id', 'latest_dataset'],

      watch: {},
      mounted() {

      },

      data() {
        return {
          is_open: false
        }
      },

      methods: {
        open() {
          this.is_open = true;
        }
      }
    }
  ) </script>
