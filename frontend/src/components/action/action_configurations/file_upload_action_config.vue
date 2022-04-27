<template>
  <v-container fluid>
    <h2>When Uploading to Which Datasets?</h2>
    <directory_list
      class="pt-2"
      :project_string_id="project_string_id"
      @directories-updated="on_directories_updated"
    ></directory_list>
  </v-container>
</template>

<script>
import directory_list from '../../source_control/directory_list'
export default {
  name: "file_upload_action_config",
  props:{
    action:{
      required: true
    },
    project_string_id:{
      required: true
    }
  },
  components: {
    directory_list: directory_list
  },
  computed:{
    on_directories_updated: function(){

    }
  }
}
</script>

<style scoped>

</style>
