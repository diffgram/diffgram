<template>
  <v-container fluid class="d-flex flex-column">
    <v_error_multiple :error="error"></v_error_multiple>
    <h1 class="font-weight-light">3. Confirm</h1>

    <h2 class="mt-4 mb-2">You Are about to import data from an external source into diffgram.</h2>
    <h2 class="font-weight-regular warning--text">
      <v-icon size="32" color="warning">mdi-alert</v-icon>
      If you selected files import too, it will create datasets and files in this project.
    </h2>

    <v-container v-if="stats">
      <h1 class="mb-4">Data to Import: </h1>
      <p style="font-size: 1.2rem">
        <v-icon size="32" color="success">mdi-check</v-icon>
        <strong class="secondary--text">Number of Attributes: </strong>
        <strong>{{stats.attr_count}}</strong>
      </p>
      <p style="font-size: 1.2rem">
        <v-icon size="32" color="success">mdi-check</v-icon>
        <strong class="secondary--text">Number of Global Attributes: </strong>
        <strong>{{stats.attr_global_count}}</strong>
      </p>
      <p style="font-size: 1.2rem">
        <v-icon size="32" color="success">mdi-check</v-icon>
        <strong class="secondary--text">Number of Labels: </strong>
        <strong>{{stats.labels_count}}</strong>
      </p>
      <p style="font-size: 1.2rem">
        <v-icon size="32" color="success">mdi-check</v-icon>
        <strong class="secondary--text">Number of Datasets: </strong>
        <strong>{{stats.dataset_count}}</strong>
      </p>
    </v-container>

    <div class="d-flex justify-center align-center">
      <v-btn color="success" x-large>
        <v-icon>mdi-application-import</v-icon>
        Start Project Import
      </v-btn>
    </div>
  </v-container>
</template>

<script lang="ts">

import migration_config_labelbox from './migration_config_labelbox';
import {fetch_project_stats_labelbox} from '../../services/labelboxConnectionServices'
import Vue from "vue";

export default Vue.extend({
    name: 'project_migrator_confirm_step',
    components: {
      migration_config_labelbox
    },
    props: {
      project_string_id: {
        default: null
      },
      project_migration_data: {
        default: null
      }
    },
    data() {
      return {
        step: 2,
        loading_steps: false,
        stats: {},
        error: null,
      }
    },
    watch:{
      project_migration_data:{
        deep: true,
        handler: async function(){
          await this.fetch_project_stats_labelbox();
        }
      },
    },
    mounted: async function () {
      await this.fetch_project_stats_labelbox();
    },
    computed: {},
    methods: {
      fetch_project_stats_labelbox: async function () {
        if (!this.project_migration_data.labelbox_project_id) {
          return
        }
        let labelbox_project_id = this.project_migration_data.labelbox_project_id;
        let [result, error] = await fetch_project_stats_labelbox(this.project_migration_data.connection.id, labelbox_project_id);
        console.log('stats', result)
        if(error){
          this.error = this.$route_api_errors(error);
          return
        }
        this.stats = result.result;
      },
      on_next_button_click: function () {
        this.$emit('next_step');
      }
    }
  }
) </script>
