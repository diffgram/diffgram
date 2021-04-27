<template>
  <cloud_storage_searchbar
    v-if="connection && $store.state.connection.connection_list.length > 0 && connection.integration_name === 'google_gcp'"
    :project_string_id="project_string_id"
    label="Google Cloud Storage path"
    ref="google_gcp"
    @update_bucket_name="update_bucket_name"
    :connection="connection"
    :video_split_duration="video_split_duration"
    :job_id="job_id"
  ></cloud_storage_searchbar>
  <cloud_storage_searchbar
    v-else-if="connection && $store.state.connection.connection_list.length > 0 && connection.integration_name === 'amazon_aws'"
    :project_string_id="project_string_id"
    ref="amazon_aws"
    label="Amazon AWS S3 path"
    :connection="connection"
    @update_bucket_name="update_bucket_name"
    :video_split_duration="video_split_duration"
    :job_id="job_id"
  ></cloud_storage_searchbar>
  <cloud_storage_searchbar
    v-else-if="connection && $store.state.connection.connection_list.length > 0 && connection.integration_name === 'microsoft_azure'"
    :project_string_id="project_string_id"
    ref="microsoft_azure"
    label="Azure Blob Storage path"
    :connection="connection"
    @update_bucket_name="update_bucket_name"
    :video_split_duration="video_split_duration"
    :job_id="job_id"
  ></cloud_storage_searchbar>
</template>

<script>
  import {debounce} from "debounce";
  import {mapState} from 'vuex'
  import cloud_storage_searchbar from "./cloud_storage_searchbar";

  export default {
    components: {cloud_storage_searchbar},
    props: {
      'project_string_id' : {
        default: null
      },
      'connection' : {    // or could do 'value' if we wanted it more generic
        default: null,
        type: Object
      },
      'video_split_duration':{
        default: undefined,
        type: Number
      },
      'job_id':{
        default: undefined,
        type: Number
      }
    },
    name: "connector_import_renderer",
    created() {

    },
    data() {
      return {
        bucket: undefined
      }
    },
    methods: {
      update_bucket_name: function(name){
        this.bucket = name;
        this.$emit('update_bucket_name', name)
      }
    },
    computed:{
    }
  }
</script>

<style scoped>
  .v-list-item--link::before {
    background-color: red;
  }
</style>
