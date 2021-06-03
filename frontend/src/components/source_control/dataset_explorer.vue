<template>
  <v-layout column>
    <v-toolbar extended elevation="0">
      <v-toolbar-title class="d-flex align-center">
        <v-icon x-large>mdi-folder-home</v-icon>Projects/{{project_string_id}}/Datasets/
      </v-toolbar-title>
      <div class="d-flex align-center">
        <v_directory_list :project_string_id="project_string_id"
                          @change_directory="on_change_ground_truth_dir"
                          ref="ground_truth_dir_list"
                          class="mt-5"
                          :change_on_mount="true"
                          :show_new="false"
                          :initial_dir_from_state="false"
                          :update_from_state="false"
                          :set_current_dir_on_change="false"
                          :view_only_mode="false"
                          :show_update="false"
                          :set_from_id="$store.state.project.current_directory.directory_id">
        </v_directory_list>
      </div>
      <v-spacer></v-spacer>

      <v-btn icon>
        <v-icon>mdi-filter</v-icon>
      </v-btn>

      <v-btn icon>
        <v-icon>mdi-dots-vertical</v-icon>
      </v-btn>
    </v-toolbar>
    <v-layout fluid class="d-flex flex-wrap">

      <v-progress-linear indeterminate v-if="loading"></v-progress-linear>
      <file_preview
        v-else
        v-for="(file, index) in this.file_list"
        :key="file.id"
        :project_string_id="project_string_id"
        :file="file"
        :instance_list="file.instance_list"
      ></file_preview>

    </v-layout>

  </v-layout>
</template>

<script>
  import Vue from "vue";
  import axios from "axios";

  import file_preview from "./file_preview";
  export default Vue.extend({
    name: "dataset_explorer",
    components:{
      file_preview,
    },
    props: [
      'project_string_id',

    ],
    mounted() {
      if(!this.metadata.directory_id){
        this.metadata.directory_id = this.$store.state.project.current_directory.directory_id;
      }
      this.fetch_file_list();
    },
    data: function () {
      return {
        file_list: [],
        loading: false,
        metadata: {
          'directory_id': undefined,
          'limit': this.metadata_limit,
          'media_type': this.filter_media_type_setting,
          'page_number': this.page_number,
          'request_next_page': false,
          'request_previous_page' : false,
          'file_view_mode': 'explorer',
          'previous': undefined,
          'search_term': this.search_term
        }

      }
    },
    methods: {
      fetch_file_list: async function(){
        this.loading = true
        try{
          console.log('metaa', this.metadata)
          const response = await axios.post('/api/project/' + String(this.$props.project_string_id) +
            '/user/' + this.$store.state.user.current.username + '/file/list', {
            'metadata': this.metadata,
            'project_string_id': this.$props.project_string_id

          })
          if (response.data['file_list'] != null) {
            this.file_list = response.data.file_list;
          }
        }
        catch (error) {
          console.error(error);
        }
        finally {
          this.loading = false;
        }

      },
      on_change_ground_truth_dir: function(dir){
        console.log('changee', this.$store.state.project)
        this.metadata.directory_id = dir.id;

      }
    }

  })
</script>

<style scoped>

</style>
