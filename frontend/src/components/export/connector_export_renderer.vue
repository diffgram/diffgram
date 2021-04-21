<template>
  <export_storage_searchbar
    v-if="connection && connection.integration_name === 'google_gcp'"
    :project_string_id="project_string_id"
    :export_obj="export_obj"
    label="Google Cloud Storage path"
    :connection="connection"
    @folder-selected="on_folder_selected"
    ref="google_gcp"
    :format="format"
  ></export_storage_searchbar>
  <export_storage_searchbar
    v-else-if="connection && connection.integration_name === 'amazon_aws'"
    :project_string_id="project_string_id"
    :export_obj="export_obj"
    label="Amazon AWS S3 path"
    ref="amazon_aws"
    @folder-selected="on_folder_selected"
    :connection="connection"
    :format="format"
  ></export_storage_searchbar>
  <export_storage_searchbar
    v-else-if="connection && connection.integration_name === 'microsoft_azure'"
    :project_string_id="project_string_id"
    :export_obj="export_obj"
    label="Azure container path"
    ref="microsoft_azure"
    @folder-selected="on_folder_selected"
    :connection="connection"
    :format="format"
  ></export_storage_searchbar>
</template>

<script>
  import {debounce} from "debounce";
  import {mapState} from 'vuex'
  import export_storage_searchbar from "./export_storage_searchbar";

  export default {
    components: {export_storage_searchbar},
    props: {
      'project_string_id' : {
        default: null
      },
      'connection' : {    // or could do 'value' if we wanted it more generic
        default: null,
        type: Object
      },
      'export_obj': {
        default: null,
        type: Object
      },
      'format':{
        type: String,
        default: 'JSON'
      }
    },
    name: "connector_export_renderer",
    data() {
      return {
        current_ref: ''
      }
    },
    methods: {
      async export_start(){
        return await this.$refs[this.connection.integration_name].start_export();
      },
      get_selected_items(){
        if(this.$refs[this.connection.integration_name]){
          return this.$refs[this.connection.integration_name].selected;
        }
        return false;
      },
      on_folder_selected(selection){
        this.$emit('folder-selected', selection)
      }
    },
    watch: {
      search_folder: debounce(async function () {
        this.do_folder_search();
      }, 500),
    }
  }
</script>

<style scoped>
  .v-list-item--link::before {
    background-color: red;
  }
</style>
