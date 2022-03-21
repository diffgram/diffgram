<template>
  <v-container fluid class="d-flex flex-column">
    <v_error_multiple :error="error"></v_error_multiple>
    <div class="d-flex align-center">
      <img width="200"
           height="50px"
           src="data:image/png;base64,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"
           alt="">
    </div>
    <h4>1. Select Labelbox Project: </h4>
    <v-select @change="on_project_selected" item-text="name" item-value="id" :items="labelbox_projects" v-model="project_migration_data.labelbox_project_id"></v-select>
    <v-checkbox label="Import Schema" disabled v-model="project_migration_data.import_schema"></v-checkbox>
    <v-checkbox label="Import Files (Images Only)" v-model="project_migration_data.import_files"></v-checkbox>
  </v-container>
</template>

<script lang="ts">

import connection_select from '../connection/connection_select';
import {getLabelboxProjectList} from '../../services/labelboxConnectionServices'
import Vue from "vue";

export default Vue.extend({
    name: 'migration_config_labelbox',
    components: {
      connection_select
    },
    props: {
      project_string_id: {
        default: null
      },
      project_migration_data: {
        default: {
          import_schema: true,
          import_files: false,

        },
        required: true
      }
    },
    data() {
      return {
        labelbox_projects: [],
        error: null,
      }
    },
    computed: {},
    async mounted() {
      await this.get_labelbox_projects();
    },
    methods: {
      on_project_selected: function(val){
        this.project_migration_data.labelbox_project_id = val;
      },
      get_labelbox_projects: async function () {
        if(!this.project_migration_data){
          return
        }
        if(!this.project_migration_data.connection){
          return
        }
        const [data, error] = await getLabelboxProjectList(this.project_migration_data.connection.id);
        if(error){
          this.error = this.$route_api_errors(error)
          return
        }
        this.labelbox_projects = data.result;

      },
    }
  }
) </script>
