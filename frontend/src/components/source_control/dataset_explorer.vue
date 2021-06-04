<template>
  <v-layout column>
    <v-toolbar extended elevation="0" class="ma-8">
      <v-toolbar-title class="d-flex align-center">
        <v-icon x-large>mdi-folder-home</v-icon>Projects/{{project_string_id}}/Datasets/
      </v-toolbar-title>
      <div class="d-flex align-center mr-5">
        <v_directory_list :project_string_id="project_string_id"
                          @change_directory="on_change_ground_truth_dir"
                          ref="ground_truth_dir_list"
                          class="mt-5"
                          :change_on_mount="true"
                          :show_new="false"
                          :initial_dir_from_state="true"
                          :update_from_state="false"
                          :set_current_dir_on_change="false"
                          :view_only_mode="false"
                          :show_update="false"
                          :set_from_id="directory.directory_id">
        </v_directory_list>
      </div>
      <div class="d-flex align-center align-content-center">

        <h4 class="mt-4 mr-4 mb-3">Compare Inferences: </h4>
        <model_run_selector
          class="mt-4"
          :multi_select="false"
          :model_run_list="model_run_list"
          @model_run_change="update_base_model_run"
          :project_string_id="project_string_id">

        </model_run_selector>
        <h2 class="font-weight-light mr-4 ml-4">VS</h2>
        <model_run_selector
          class="mt-4"
          :multi_select="true"
          :model_run_list="model_run_list"
          @model_run_change="update_compare_to_model_runs"
          :project_string_id="project_string_id">

        </model_run_selector>
        <div class="mt-4 ml-4">
          <v-switch
            v-model="show_ground_truth"
            :label="`Show Ground Truth`"
          ></v-switch>
        </div>
      </div>
      <v-spacer></v-spacer>

      <v-btn icon>
        <v-icon>mdi-filter</v-icon>
      </v-btn>

      <v-btn icon>
        <v-icon>mdi-dots-vertical</v-icon>
      </v-btn>
    </v-toolbar>
    <v-layout fluid class="d-flex flex-wrap" style="min-height: 300px">

      <v-progress-linear indeterminate v-if="loading"></v-progress-linear>
      <file_preview
        v-else
        v-for="(file, index) in this.file_list"
        :base_model_run="base_model_run"
        :compare_to_model_run_list="compare_to_model_run_list"
        :key="file.id"
        :project_string_id="project_string_id"
        :file="file"
        :instance_list="file.instance_list"
        :show_ground_truth="show_ground_truth"
        @view_file_detail="view_detail"
      ></file_preview>

    </v-layout>

  </v-layout>
</template>

<script>
  import Vue from "vue";
  import axios from "axios";
  import directory_icon_selector from '../source_control/directory_icon_selector'
  import model_run_selector from "../model_runs/model_run_selector";
  import file_preview from "./file_preview";
  export default Vue.extend({
    name: "dataset_explorer",
    components:{
      model_run_selector,
      directory_icon_selector,
      file_preview,
    },
    props: [
      'project_string_id',
      'directory'

    ],
    mounted() {
      if(!this.metadata.directory_id){
        this.metadata.directory_id = this.$props.directory.directory_id;
        this.selected_dir = this.$props.directory;
      }
      this.fetch_file_list();
      this.fetch_model_run_list();
    },
    data: function () {
      return {
        file_list: [],
        model_run_list: [],
        loading: false,
        show_ground_truth: false,
        selected_dir: undefined,
        base_model_run: undefined,
        compare_to_model_run_list: undefined,
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
    watch:{
      selected_dir: function () {
        this.fetch_file_list();
      }
    },
    methods: {
      update_compare_to_model_runs: function(value){
        this.compare_to_model_run_list = value
      },
      update_base_model_run: function(value){
        this.base_model_run = value
      },
      fetch_file_list: async function(){
        this.loading = true
        try{
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
      fetch_model_run_list: async function(){
        this.loading = true
        try{
          const response = await axios.post(
            `/api/v1/project/${this.$props.project_string_id}/model-runs/list`,
            {}
          );
          if (response.data['model_run_list'] != undefined) {
            this.model_run_list = response.data.model_run_list;
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
        this.selected_dir = dir;

      },
      view_detail: function(file){
        this.$emit('view_detail', file)
      }
    }

  })
</script>

<style scoped>

</style>
