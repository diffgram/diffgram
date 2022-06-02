<template>

  <v-dialog v-model="is_open" id="input_payload" :click:outside="close">
    <v-card elevation="1">
      <v-card-title>Log:</v-card-title>
      <v-card-text v-if="project_migration">
       <v_error_multiple :error="project_migration.error_log"></v_error_multiple>
       <v_info_multiple :info="project_migration.migration_log"
                        :dismissible="false"></v_info_multiple>
      </v-card-text>
    </v-card>
  </v-dialog>

</template>

<script lang="ts">

import Vue from "vue";
export default Vue.extend({

    name: 'project_migration_error_dialog',
    props: ['project_migration'],

    data() {
      return {
        loading: false,
        is_open: false,
      }
    },
    watch: {

    },

    methods: {
      close() {
        this.is_open = false;
      },
      open() {
        this.is_open = true;
      },
    }
  }
) </script>
