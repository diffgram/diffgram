<template>
  <v-container fluid class="d-flex flex-column align-center justify-center" style="min-height: 600px">

    <div v-if="progress_percentage < 100 && status === 'in_progress'" class="d-flex flex-column align-center justify-center" style="width: 100%">
      <h1 class="pa-4">Importing...</h1>
      <p>You may close this window without effecting the import.
         This may take several minutes.
         This screen will automatically update, or you can view the status on the list page. </p>
      <v-progress-linear
        color="secondary"
        striped
        :value="progress_percentage"
        height="85"
      >
        <h1 class="white--text"> {{progress_percentage.toFixed(2)}} %</h1>
      </v-progress-linear>

    </div>
    <div style="width: 100%" v-else-if="progress_percentage >= 100" class="d-flex flex-column align-center justify-center">
      <v-icon size="256" color="success">mdi-check-decagram</v-icon>
      <h1 class="ma-8">Data Succesfully Migrated into Diffgram.</h1>
      <v-btn x-large @click="$router.push(`/project/${project_string_id}/labels?schema_id=${project_migration.label_schema_id}`)" color="primary">
        <v-icon>mdi-format-list-bulleted</v-icon>
        View Migrated Labels
      </v-btn>
    </div>

    <div style="width: 100%" v-else-if="status === 'failed'" class="d-flex flex-column align-center justify-center">
      <v-icon size="256" color="error">mdi-alert</v-icon>
      <h1 class="ma-8">Migration Failed.</h1>
      <v-btn x-large @click="$router.push(`/project/${project_string_id}/project-migrations`)" color="primary">
        <v-icon>mdi-format-list-bulleted</v-icon>
        View Migrations History
      </v-btn>
      <v-btn class="mt-4" @click="retry_migration" color="warning">
        <v-icon>mdi-refresh</v-icon>
        Retry
      </v-btn>
    </div>
    <error_multiple :error="error"></error_multiple>
  </v-container>
</template>

<script lang="ts">

import migration_config_labelbox from './migration_config_labelbox';
import {get_project_migration} from '../../services/projectMigrationServices'
import Vue from "vue";
import Error_multiple from "../regular/error_multiple.vue";

export default Vue.extend({
    name: 'project_migrator_confirm_step',
    components: {
      Error_multiple,
      migration_config_labelbox
    },
    props: {
      project_string_id: {
        default: null
      },
      project_migration_id: {
        default: null
      },
    },
    data() {
      return {
        step: 2,
        progress_percentage: 0,
        project_migration: null,
        uploading: false,
        error: null,
        interval: null,
        loading: false,
        status: 'in_progress',

      }
    },
    watch:{

    },
    mounted: async function () {
      this.update_migration_status();
    },
    beforeDestroy() {
      clearInterval(this.interval)
    },
  computed: {},
    methods: {
      retry_migration: function(){
        this.error = {}
        this.status = 'in_progress';
        this.$emit('retry_migration')
      },
      update_migration_status: async function(){

        this.interval = setInterval(async () =>{
          let [project_migration_data, err] = await get_project_migration(this.project_string_id, this.project_migration_id)
          if(err){
            this.error = this.$route_api_errors(err);
            return
          }
          this.progress_percentage =  project_migration_data.percent_complete;
          if(this.progress_percentage >= 100){
            this.$emit('migration_finished')
          }
          this.project_migration = project_migration_data;
          if(this.project_migration.status === 'failed'){
            this.status = 'failed';
            this.error = this.project_migration.error_log
          }

        }, 2000)

      }
    }
  }
) </script>
