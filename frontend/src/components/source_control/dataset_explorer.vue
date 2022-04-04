<template>
  <v-layout>
  <v-sheet
      class="pl-4 pt-2"
      style="border-right: 1px solid #e0e0e0;border-top: 1px solid #e0e0e0; min-width:400px"
      >
      <v_error_multiple :error="query_error"></v_error_multiple>

      <v-layout>
      <v-menu :value="query_menu_open"
              :offset-y="true"
              :close-on-content-click="false"
              :close-on-click="false"
              z-index="99999999"
              >
        <template v-slot:activator="{ on, attrs }">
          <v-text-field
            class="pt-4"
            label="Query your data: "
            v-model="query"
            data-cy="query_input_field"
            @focus="on_focus_query"
            @blur="on_blur_query"
            @keydown.enter="execute_query($event.target.value)"
          ></v-text-field>
        </template>
        <query_suggestion_menu
          ref="query_suggestions"
          @update_query="update_query"
          @close="close_suggestion_menu"
          @execute_query="execute_query"
          :project_string_id="project_string_id"
          :query="query" ></query_suggestion_menu>
      </v-menu>
 
        <tooltip_button
          tooltip_message="Refresh"
          datacy="refresh_explorer"
          @click="fetch_file_list"
          icon="refresh"
          :icon_style="true"
          color="primary"
        >
        </tooltip_button>
      </v-layout>

      <v_directory_list :project_string_id="project_string_id"
                        @change_directory="on_change_ground_truth_dir"
                        ref="ground_truth_dir_list"
                        :change_on_mount="true"
                        :show_new="false"
                        :initial_dir_from_state="true"
                        :update_from_state="false"
                        :set_current_dir_on_change="false"
                        :view_only_mode="false"
                        :show_update="false"
                        :set_from_id="current_dir_id">
      </v_directory_list>

      <v-switch
        class="pr-4"
        v-model="show_ground_truth"
        :label="`Show Ground Truth`"
      ></v-switch>

      <v-switch
        v-model="compare_models"
        :label="`Compare Models`"
      ></v-switch>
    
<!--      <v-btn icon disabled>-->
<!--        <v-icon>mdi-filter</v-icon>-->
<!--      </v-btn>-->

    <div v-if="compare_models == true">
      <v-layout column>
        <h4 class="mt-4 mr-4 mb-3">Compare Inferences: </h4>
        <model_run_selector
          class="mt-4"
          :multi_select="false"
          :model_run_list="model_run_list"
          @model_run_change="update_base_model_run"
          :project_string_id="project_string_id">

        </model_run_selector>
        <h2 class="font-weight-light">VS</h2>
        <model_run_selector
          class="mt-4"
          :multi_select="true"
          :model_run_list="model_run_list"
          @model_run_change="update_compare_to_model_runs"
          :project_string_id="project_string_id">

        </model_run_selector>
      </v-layout>
    </div>

  </v-sheet>

  <v-sheet style="border-right: 1px solid #e0e0e0;border-top: 1px solid #e0e0e0; min-width:600px">
    <v-progress-linear indeterminate
                       v-if="loading"
                       height="10"
                       attach
                       class="d-flex flex-column align-center justify-center ma-0">
    </v-progress-linear>

    <v-container v-if="none_found == true && metadata && metadata.page == 1"
                 fluid style="border: 1px solid #ababab"
                 class="d-flex flex-column align-center justify-center ma-0">
      <h1 class="pt-4">No Results</h1>
      <v-icon class="pt-4" size="250">mdi-magnify</v-icon>
    </v-container>

    <v-layout id="infinite-list"
              fluid
              class="files-container d-flex justify-start"
              data-cy="file_review_container"
              :style="{height: full_screen ? '760px' : '350px', overflowY: 'auto', ['flex-flow']: 'row wrap', oveflowX: 'hidden'}">


      <file_preview
        class="file-preview"
        v-if="file_list && file_list.length > 0"
        v-for="(file, index) in file_list"
        :base_model_run="base_model_run"
        :compare_to_model_run_list="compare_to_model_run_list"
        :key="file.id"
        :project_string_id="project_string_id"
        :file="file"
        :instance_list="file.instance_list"
        :show_ground_truth="show_ground_truth"
        @view_file_detail="view_detail"
      ></file_preview>
      <v-container fluid v-else-if="this.file_list.length === 0" class="d-flex flex-column justify-center">
        <h1 class="text-center">There are no files available</h1>
        <v-icon class="text-center" size="86">mdi-text-box-search-outline</v-icon>
      </v-container>


    </v-layout>
    <v-snackbar indeterminate v-if="infinite_scroll_loading">.
      Loading...<v-progress-circular indeterminate></v-progress-circular>
    </v-snackbar>

    <v-container v-if="none_found == true && metadata && metadata.page > 1"
                 fluid style="border: 1px solid #ababab"
                 class="d-flex flex-column align-center justify-center ma-0">
      <h1 class="pt-4">End of Results</h1>
      <v-icon class="pt-4" size="250">mdi-magnify</v-icon>
    </v-container>
  
   </v-sheet>  
  </v-layout>
</template>

<script>
  import Vue from "vue";
  import axios from "../../services/customInstance";
  import directory_icon_selector from '../source_control/directory_icon_selector'
  import model_run_selector from "../model_runs/model_run_selector";
  import query_suggestion_menu from "./query_suggestion_menu";

  export default Vue.extend({
    name: "dataset_explorer",
    components:{
      model_run_selector,
      directory_icon_selector,
      query_suggestion_menu,
    },
    props: [
      'project_string_id',
      'project_string_id',
      'directory',
      'full_screen'

    ],
    mounted() {
      if (window.Cypress) {
        window.DatasetExplorer = this;
      }
      if(!this.metadata.directory_id){
        this.metadata.directory_id = this.$props.directory.directory_id;

        this.selected_dir = this.$props.directory;
      }
      if(this.$props.directory){
        this.current_dir_id = this.$props.directory.directory_id;
      }
      if(this.$route.query.directory_id){
        this.current_dir_id = this.$route.query.directory_id;
      }
      if(this.$route.query.query){
        this.query = this.$route.query.query;
      }
      this.fetch_file_list(true);
      this.fetch_model_run_list();
      // Detect when scrolled to bottom.
      const listElm = document.querySelector('#infinite-list');
      listElm.addEventListener('scroll', e => {
        if(listElm.scrollTop + listElm.clientHeight >= listElm.scrollHeight) {
          if(this.file_list.length > 0){
            this.load_more_files();
          }

        }
      });
    },
    data: function () {
      return {
        file_list: [],
        model_run_list: [],
        metadata_previous: {
          file_count: null
        },
        loading: false,
        query: undefined,
        query_error: undefined,
        current_dir_id: null,
        show_ground_truth: true,
        infinite_scroll_loading: false,
        loading_models: false,
        none_found: undefined,
        query_menu_open: false,
        selected_dir: undefined,
        compare_models: false,
        base_model_run: undefined,
        compare_to_model_run_list: undefined,
        metadata: {
          'directory_id': undefined,
          'limit': 28,
          'media_type': this.filter_media_type_setting,
          'page': 1,
          'query_menu_open' : false,
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
      update_query: function(value){
        if(!this.query){
          this.query = value;
        }
        else{
          this.query += value;
        }
      },
      on_focus_query: function(){
        this.$store.commit('set_user_is_typing_or_menu_open', true);
        this.query_menu_open = true
      },
      on_blur_query: function(){
        this.$store.commit('set_user_is_typing_or_menu_open', false)
      },
      execute_query: async function(query_str){
        this.query_menu_open = false;
        this.query = query_str;
        this.file_list = []
        await this.fetch_file_list(true)
      },
      close_suggestion_menu: async function(query_str){
        this.query_menu_open = false;
      },
      load_more_files: async function(){
        this.metadata.page += 1;
        await this.fetch_file_list(false)
      },
      update_compare_to_model_runs: function(value){
        this.compare_to_model_run_list = value
      },
      update_base_model_run: function(value){
        this.base_model_run = value
      },
      fetch_file_list: async function(reload_all = true){
        if(reload_all){
          this.metadata.page = 1;
          this.loading = true
        }
        else{
          this.infinite_scroll_loading = true;
        }
        try{
          this.none_found = undefined
          const response = await axios.post('/api/project/' + String(this.$props.project_string_id) +
            '/user/' + this.$store.state.user.current.username + '/file/list', {
            'metadata': {
              ...this.metadata,
              query: this.query,
              previous: this.metadata_previous
            },
            'project_string_id': this.$props.project_string_id

          })
          if (response.data['file_list'] == false) {
            this.none_found = true
          }
          else {
            if(reload_all){
              this.file_list = response.data.file_list;
            }
            else{

              for(const file in response.data.file_list){
                if(!this.file_list.find(f => f.id === file.id)){
                  this.file_list.push(file);
                }
              }
              this.file_list = this.file_list.concat(response.data.file_list);
            }

          }
          this.metadata_previous = response.data.metadata;
        }
        catch (error) {
          console.error(error);
          this.query_error = this.$route_api_errors(error)
        }
        finally {
          if(reload_all){
            this.loading = false;
          }
          else{
            this.infinite_scroll_loading = false;
          }

        }
      },
      fetch_model_run_list: async function(){
        this.loading_models = true
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
          this.loading_models = false;
        }

      },
      on_change_ground_truth_dir: function(dir){
        this.file_list = [];
        this.metadata.directory_id = dir.directory_id;
        this.selected_dir = dir;

      },
      view_detail: function(file, model_runs, color_list){
        this.$emit('view_detail', file, model_runs, color_list)
      }
    }

  })
</script>

<style>

  .files-container::after {
    content: "";
    flex: auto;
  }

  .v-text-field input {
    font-size: 1.5em;
  }
</style>
