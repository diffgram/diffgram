<template>
  <v-container fluid class="d-flex flex-column">
    <h1 class="font-weight-light">Configure </h1>

    <migration_config_labelbox
      ref="labelbox_config"
      @project_selected="on_project_selected"
      :project_string_id="project_string_id"
      :project_migration_data="project_migration_data"
      v-if="project_migration_data.connection && project_migration_data.connection.integration_name === 'labelbox'">
    </migration_config_labelbox>

    <label_schema_selector
      :project_string_id="project_string_id"
      label="Select Diffgram Label Schema"
      @change="change_label_schema($event)"
    >
    </label_schema_selector>

    <wizard_navigation
      @next="on_next_button_click"
      :loading_next="loading_steps"
      :disabled_next="loading_steps || !project_migration_data.labelbox_project_id"
      @back="$emit('previous_step')"
      :skip_visible="false"
    >
    </wizard_navigation>

  </v-container>
</template>

<script lang="ts">

import migration_config_labelbox from './migration_config_labelbox';
import label_schema_selector from '../label/label_schema_selector.vue';
import {get_schemas} from "../../services/labelServices";

import Vue from "vue";
export default Vue.extend( {
  name: 'project_migrator_config_step',
  components:{
    migration_config_labelbox,
    label_schema_selector
  },
  props:{
    project_string_id:{
      default: null
    },
    project_migration_data:{
      default: null
    },
  },
  data() {
    return {
      step: 2,
      loading_steps: false,
      current_label_schema: null
    }
  },
  computed: {

  },
  async mounted () {
    await this.fetch_schemas()
  },
  watch:{
    project_migration_data:{
      deep: true,
      handler: function(){
        this.refresh_config_data()
      }
    }
  },
  methods: {
    on_project_selected: function(){

    },
    refresh_config_data: function(){
      if(!this.$refs.labelbox_config){
        return
      }
      if(this.project_migration_data.connection &&
        this.project_migration_data.connection.integration_name === 'labelbox'){
        this.$refs.labelbox_config.get_labelbox_projects();
      }

    },

    fetch_schemas: async function(){
      let [result, error] = await get_schemas(this.project_string_id);
      if(error){
        this.error = this.$route_api_errors(error)
      }
      if(result){
        this.label_schema_list = result;
      }
    },

    change_label_schema: function (schema) {

      this.project_migration_data.label_schema_id = schema.id
      console.log(schema)
      this.current_label_schema = schema;
    },

    on_next_button_click: function(){
      this.$emit('next_step');
    }
  }
}

) </script>
