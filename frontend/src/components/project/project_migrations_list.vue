<template>
  <v-container fluid  style="min-height: 600px; width: 100%">
  <v-card width="100%">
    <v-card-title>Project Migrations Log</v-card-title>
    <v_error_multiple :error="error"></v_error_multiple>
    <regular_table
      :loading="loading"
      :item_list="project_migration_list"
      :column_list="columns_project_migrations"
      :elevation="0"
      :items_per_page="50"
      v-model="selected_cols"
      :header_list="headers_project_migration">

      <template slot="project_migration" slot-scope="props">
        <h4 class="font-weight-light">{{props.item.created_time}} <strong>ID: {{props.item.id}}</strong> </h4>
      </template>
      <template slot="status" slot-scope="props">
        <v-progress-linear
          height="35px"
          style="max-width: 125px"
          striped
          rounded
          color="secondary"
          v-if="props.item.status === 'in_progress'"
          :value="props.item.percent_complete">
          <strong class="white--text">{{props.item.percent_complete.toFixed(1)}}</strong>
        </v-progress-linear>
        <v-icon v-else-if="props.item.status === 'success'" color="success">mdi-check-decagram</v-icon>
        <v-icon v-else-if="props.item.status === 'failed'" color="error">mdi-alert</v-icon>
      </template>
      <template slot="details" slot-scope="props">
          <div class="d-flex flex-column">
            <ul>
              <li >
                <a class="secondary--text" :href="`/connection/${props.item.connection_id}`" target="_blank">
                  Connection Name: <strong>{{props.item.connection.name}}</strong>
                </a>
              </li>
              <li v-if="props.item.description">{{props.item.description}}</li>
            </ul>
          </div>
      </template>
      <template slot="actions" slot-scope="props">
        <v-btn x-small
               :loading="migration_retry_loading[props.item.id]"
               @click="retry_migration(props.item)"
               v-if="['in_progress', 'failed'].includes(props.item.status)" color="warning">
          <v-icon>mdi-refresh</v-icon>
          Retry
        </v-btn>

        <v-btn x-small
               @click="display_error_log(props.item)"
               v-if="['failed'].includes(props.item.status)"
               color="primary">
          <v-icon>mdi-format-list-group</v-icon>
          Error Log
        </v-btn>


      </template>
    </regular_table>
  </v-card>
    <project_migrations_error_dialog
      ref="project_migration_error_dialog"
      :project_migration="selected_project_migration">

    </project_migrations_error_dialog>
  </v-container>
</template>

<script lang="ts">

import project_migrations_error_dialog from './project_migrations_error_dialog';
import {get_project_migration_list, start_project_migration} from '../../services/projectMigrationServices'
import Vue from "vue";
import Error_multiple from "../regular/error_multiple.vue";

export default Vue.extend({
    name: 'project_migrations_list',
    components: {
      Error_multiple,
      project_migrations_error_dialog
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
        headers_project_migration: [
          {
            text: "Migration",
            align: 'left',
            sortable: false,
            value: 'id'
          },
          {
            text: "Details",
            align: 'left',
            sortable: false,
            value: 'details'
          },
          {
            text: "Status",
            align: 'left',
            sortable: false,
            value: 'status'
          },
          {
            text: "Actions",
            align: 'left',
            sortable: false,
            value: 'actions'
          },
        ],
        columns_project_migrations: ['project_migration', 'details', 'status', 'actions'],
        selected_cols: [],
        project_migration_list: [],
        step: 2,
        migration_retry_loading: {},
        progress_percentage: 0,
        project_migration: null,
        uploading: false,
        error: null,
        interval: null,
        selected_project_migration: null,
        loading: false,
        status: 'in_progress',

      }
    },
    watch:{

    },
    mounted: async function () {
      await this.fetch_project_migration_list();
      await this.update_migrations_list();
    },
    beforeDestroy() {
      clearInterval(this.interval)
    },
  computed: {},
    methods: {
      display_error_log: async function(item){
        this.selected_project_migration = item;
        await this.$nextTick();
        if(!this.$refs.project_migration_error_dialog){
          return
        }
        this.$refs.project_migration_error_dialog.open();
      },
      retry_migration: async function(project_migration){
        this.migration_retry_loading[project_migration.id] = true;
        await this.$nextTick();
        let [result, error] = await start_project_migration(this.project_string_id, project_migration);
        if(error){
          this.error = this.$route_api_errors(error);
          return
        }
      },
      update_migrations_list: async function(){
        this.interval = setInterval(async ()=> {
          await this.fetch_project_migration_list()
          this.migration_retry_loading = {}
        }, 5000)
      },
      fetch_project_migration_list: async function(){
        this.loading = true;
        let [result, error] = await get_project_migration_list(this.project_string_id)
        if(error){
          this.error = this.$route_api_errors(error)
          this.loading = false;
          return
        }

        this.project_migration_list = result;
        this.loading = false;
      }
    }
  }
) </script>
