<template>
  <v-layout class="d-flex flex-column">
    <dataset_explorer_toolbar
      :loading="loading"
      :file_count="file_count"
      :selected_files="selected_files"
      :project_string_id="project_string_id"
      :query="query"
      @select_all="on_select_all"
    >

    </dataset_explorer_toolbar>
    <div class="d-flex">
      <div
        class="pt-2 overflow-y-auto"
        :style="`border-right: 1px solid #e0e0e0;border-top: 1px solid #e0e0e0; min-width:400px; max-width: 400px; height: calc(100vh - 48px);`"
      >
        <div class="mb-2" style="margin-right: auto; text-align: right; border-bottom: 1px solid #e0e0e0">
          <standard_button
            tooltip_message="Refresh"
            datacy="refresh_explorer"
            @click="fetch_file_list"
            icon="refresh"
            :icon_style="true"
            color="primary"
          >
          </standard_button>
        </div>
        <div class="pl-4" style="width: 385px;">
          <v_error_multiple :error="query_error"></v_error_multiple>


          <label_schema_selector
            :icon="false"
            :project_string_id="project_string_id"
            @change="change_schema"
          />
          <dataset_selector
            ref="ground_truth_dir_list"
            :change_on_mount="false"
            :set_current_dir_on_change="false"
            :multiple="true"
            @change_directory="dataset_change_event($event)"
          />

          <label_select_only
            :project_string_id="project_string_id"
            :schema_id="label_schema ? label_schema.id : null"
            :mode="'multiple'"
            @label_file="label_change_event($event)"
          />

          <attribute_select
            label="Global attributes"
            v-if="label_schema"
            :project_string_id="project_string_id"
            :schema_id="label_schema ? label_schema.id : null"
            :attribute_list="attribute_list"
            @attribute_change="attribute_change_event"
          />


          <tag_select
            v-model="tag_selected_list"
            :allow_new_creation="false"
            :label="'Search by tags'"
            @change="tag_change_event()"
            :clearable="true"
          />

          <v-switch
            class="pr-4"
            v-model="show_ground_truth"
            :label="`Show Ground Truth`" testing_e2e
          ></v-switch>

          <v-switch
            v-model="compare_models"
            :label="`Compare Models`"
          ></v-switch>


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

          <v-checkbox
            v-model="show_advanced_query_settings"
            :label="`Advanced query settings`"
            data-cy="advanced-query-settings"
          />

          <v-textarea
            v-if="show_advanced_query_settings"
            class="pt-4"
            label="Query your data: "
            v-model="query"
            data-cy="query_input_field"
            @focus="on_focus_query"
            @blur="on_blur_query"
            color="secondary"
            background-color="#e0e0e0"
            @keydown.enter="execute_query($event.target.value)"
          />
        </div>
      </div>

      <div style="border-top: 1px solid #e0e0e0; min-width:600px; width: 100%; overflow-y: auto">
        <v-progress-linear indeterminate
                           v-if="loading"
                           height="10"
                           attach
                           class="d-flex flex-column align-center justify-center ma-0">
        </v-progress-linear>

        <v-container v-if="none_found == true && metadata && metadata.page == 1"
                     fluid
                     style="width: 100%; min-height: 750px;  position: relative"
                     class="d-flex flex-column align-center justify-center ma-0">
          <h1 class="pt-4">No Results</h1>
          <v-icon class="pt-4" size="250">mdi-magnify</v-icon>
        </v-container>

        <v-container
          id="infinite-list"
          fluid
          ref="infinite-list"
          class="files-container d-flex flex-wrap justify-start"
          data-cy="file_review_container"
          :style="{
        height: files_container_height,
        width: '100%',
        overflowY: 'auto',
        ['flex-flow']: 'row wrap',
        position: 'absolute',
        oveflowX: 'hidden'
      }"
        >
          <file_preview
            class="file-preview"
            v-for="file in file_list"
            :base_model_run="base_model_run"
            :selectable="true"
            :compare_to_model_run_list="compare_to_model_run_list"
            :key="file.id"
            :selected="file.selected"
            :project_string_id="project_string_id"
            :file="file"
            :instance_list="file.instance_list"
            :file_preview_width="list_item_width"
            :file_preview_height="list_item_width"
            :show_ground_truth="show_ground_truth"
            @view_file_detail="view_detail"
            @file_selected="on_file_selected"
          />
        </v-container>

        <div indeterminate v-if="infinite_scroll_loading">.
          Loading...
          <v-progress-circular indeterminate></v-progress-circular>
        </div>

        <v-snackbar v-model="none_found">
          {{ none_found && metadata && metadata.page > 1 ? 'End of Results' : 'No Results' }}
        </v-snackbar>

      </div>
    </div>
  </v-layout>
</template>

<script>
  import Vue from "vue";
  import axios from "../../services/customInstance";
  import dataset_explorer_toolbar from "./dataset_explorer_toolbar";
  import directory_icon_selector from '../source_control/directory_icon_selector'
  import model_run_selector from "../model_runs/model_run_selector";
  import query_suggestion_menu from "./query_suggestion_menu";
  import label_select_only from '@/components/label/label_select_only.vue'
  import tag_select from '@/components/tag/tag_select.vue'
  import label_schema_selector from "../label/label_schema_selector.vue"
  import attribute_select from "../attribute/attribute_select.vue"
import { attribute_group_list } from "../../services/attributesService.ts";
import { get_file_signed_url } from "../../services/fileServices.ts";
import dataset_selector from "../attached/global_dataset_selector.vue"

export default Vue.extend({
  name: "dataset_explorer",
  components: {
    model_run_selector,
    directory_icon_selector,
    dataset_explorer_toolbar,
    query_suggestion_menu,
    label_select_only,
    tag_select,
    label_schema_selector,
    attribute_select,
    dataset_selector
  },
  props: [
    'project_string_id',
    'directory',
    'full_screen'
  ],
  async mounted() {
    if (window) {
      this.list_item_width = (window.innerWidth - 475) / 3
    }
    if (window.Cypress) {
      window.DatasetExplorer = this;
    }
    if (!this.metadata.directory_id) {
      this.metadata.directory_id = this.$props.directory.directory_id;

      if (this.$props.directory) this.datasets_selected.push(this.$props.directory)

      this.selected_dir = this.$props.directory;
    }
    if (this.$props.directory) {
      this.current_dir_id = this.$props.directory.directory_id;
    }
    if (this.$route.query.directory_id) {
      this.current_dir_id = this.$route.query.directory_id;
    }
    if (this.$route.query.query) {
      this.query = this.$route.query.query;
    }
    await this.fetch_file_list(true);
    await this.fetch_model_run_list();
    await this.$nextTick()
    await this.$nextTick()
    // Detect when scrolled to bottom.
    const listElm = this.$refs["infinite-list"]
    listElm.addEventListener('scroll', e => {
      if (listElm.scrollTop + listElm.clientHeight + 100 >= listElm.scrollHeight) {
        if (this.file_list.length > 0) {
          this.load_more_files();
        }

      }
    });
    window.addEventListener("keydown", this.key_down);
    window.addEventListener("keyup", this.key_up);
  },
  data: function () {
    return {
      file_list: [],
      list_item_width: 400,
      model_run_list: [],
      selected_files: [],
      metadata_previous: {
        file_count: null
      },
      show_advanced_query_settings: false,
      loading: false,
      select_all_active: false,
      query: undefined,
      query_error: undefined,
      current_dir_id: null,
      show_ground_truth: true,
      infinite_scroll_loading: false,
      ctrl_key: false,
      loading_models: false,
      none_found: undefined,
      query_menu_open: false,
      selected_dir: undefined,
      file_count: 0,
      compare_models: false,
      base_model_run: undefined,
      compare_to_model_run_list: undefined,
      cancel_request: null,
      label_schema: null,
      metadata: {
        'directory_id': undefined,
        'limit': 28,
        'media_type': this.filter_media_type_setting,
        'page': 1,
        'query_menu_open': false,
        'file_view_mode': 'explorer',
        'previous': undefined,
        'search_term': this.search_term
      },
      datasets_selected: [],
      labels_selected: [],
      attributes_selected: [],
      tag_selected_list: [],
      attribute_list: [],
    }
  },
  watch: {
    selected_dir: function () {
      this.fetch_file_list();
    },
    label_schema: function () {
      this.get_schema_attributes()
    }
  },
  computed: {
    files_container_height: function () {
      if (this.file_list.length === 0) {
        return '0px'
      }
      if (this.full_screen) {
        return `100%`
      } else {
        return 'auto'
      }
    }
  },
  methods: {
    key_down: function (event) {
      this.set_control_key(event)
    },
    key_up: function (event) {
      this.set_control_key(event)
    },
    set_control_key: function (event) {
      // Caution used name commands here to that when multiple keys are pressed it still works
      if (event.ctrlKey === false || event.metaKey === false) {
        // ctrlKey cmd key
        this.ctrl_key = false;
      }
      if(event.ctrlKey){
        this.ctrl_key = true;
      }
    },

    get_schema_attributes: async function () {
      const [data, error] = await attribute_group_list(this.project_string_id, undefined, this.label_schema.id, 'from_project')

      if (!error) {
        this.attribute_list = [...data.attribute_group_list]
      }
    },
    update_query: function (value) {
      if (!this.query) {
        this.query = value;
      } else {
        this.query += value;
      }
    },

    refresh_query: function () {

      let new_query = this.generate_query()
      this.query = new_query
      this.execute_query(new_query)

    },

    generate_query: function () {

      let query = ""

      let dir_list_query = this.generate_directory_list_query(this.datasets_selected)
      if (dir_list_query) {
        query += dir_list_query
      }

      let label_query = this.generate_label_query(this.labels_selected)
      if (label_query) {
        if (dir_list_query) {
          query += " and "
        }
        query += label_query
      }

      let attribute_query = this.generate_attribute_query(this.attributes_selected)
      if (attribute_query) {
        if (dir_list_query || label_query) {
          query += " and "
        }
        query += attribute_query
      }

      return query

    },

    generate_directory_list_query: function (datasets_selected) {

      if (!Array.isArray(datasets_selected)) {
        return
      }
      if (datasets_selected.length === 0) {
        return
      }

      let query = "dataset.id in ["

      for (let dataset of datasets_selected) {
        let id = (dataset.id || dataset.directory_id)
        query += id
        query += ","
      }

      if (datasets_selected.length >= 1) {
        query = query.slice(0, -1) // remove trailing comma
      }

      query += "]"

      return query

    },

    generate_label_query: function (labels_selected) {

      if (labels_selected.length === 0) {
        return
      }

      let query = ""

      for (let label of labels_selected) {
        query += "labels."
        query += label.label.name
        query += " >= 1"
        query += " and "
      }

      if (labels_selected.length === 1 || labels_selected.length >= 1) {
        query = query.slice(0, -4) // remove trailing
      }

      return query

    },
    generate_attribute_query: function (attributes_selected) {
      let attribute_query = ""
      attributes_selected.map((attribute, index) => {
        if (attribute.kind === 'select' || attribute.kind === 'radio') {
          attribute_query += `attributes.${attribute.prompt.replaceAll(' ', '_')} = ${attribute.value[0].id}`
        } else if (attribute.kind === 'multiple_select' || attribute.kind === 'tree') {
          attribute_query += `attributes.${attribute.prompt.replaceAll(' ', '_')} in ${JSON.stringify(attribute.value.map(value => value.id))}`
        } else if (attribute.kind === 'time' || attribute.kind === 'slider' || attribute.kind === 'date' || attribute.kind === 'text') {
          const value = attribute.kind === 'text' ? `"${attribute.value}"` : attribute.value
          attribute_query += `attribute.${attribute.prompt.replaceAll(' ', '_')} = ${value}`
        }
        if (attributes_selected.length > index + 1) {
          attribute_query += " and "
        }
      })
      return attribute_query
    },

    tag_change_event: function () {
      this.refresh_query()

    },
    attribute_change_event: function (event) {
      const attribute = event[0]
      const attribute_value = event[1]

      let working_attribute;
      let values;

      const attribute_exists = this.attributes_selected.find(attr => attr.id === attribute.id)

      if (attribute_exists) working_attribute = attribute_exists
      else working_attribute = {...attribute}

      if (attribute.kind === 'select' || attribute.kind === 'radio') {
        values = [{...attribute_value}]
      } else if (
        attribute.kind === 'multiple_select' ||
        attribute.kind === 'time' ||
        attribute.kind === 'slider' ||
        attribute.kind === 'date' ||
        attribute.kind === 'text'
      ) {
        values = attribute_value
      } else if (attribute.kind === 'tree') {
        const attribute_keys = Object.keys(attribute_value)
        const tree_values = attribute_keys.map(key => ({id: parseInt(key), ...attribute_value[key]}))
        values = tree_values
      }

      working_attribute.value = values

      if (!attribute_exists) this.attributes_selected.push(working_attribute)

      this.attributes_selected = this.attributes_selected.filter(attribute => {
        if (!attribute.value) return false
        if (Array.isArray(attribute.value) && attribute.value.length === 0) return false
        return true
      })

      this.refresh_query()
    },

    label_change_event: function (label_file_list) {
      this.labels_selected = label_file_list
      this.refresh_query()
    },

    dataset_change_event: function (datasets_selected) {

      this.datasets_selected = datasets_selected
      this.refresh_query()

    },
    on_select_all: function(){
      this.select_all_active = !this.select_all_active
      if(this.select_all_active) {
        this.selected_files = []
        for (let file_elm of this.file_list) {
          file_elm.selected = true;
          this.selected_files.push(file_elm)
        }
      }
      else{
        this.selected_files = []
        for (let file_elm of this.file_list) {
          file_elm.selected = false;
        }
      }

    },
    on_focus_query: function () {
      this.$store.commit('set_user_is_typing_or_menu_open', true);
      this.query_menu_open = true
    },
    on_blur_query: function () {
      this.$store.commit('set_user_is_typing_or_menu_open', false)
    },
    execute_query: async function (query_str) {
      this.query_menu_open = false;
      this.query = query_str;
      this.file_list = []
      await this.fetch_file_list(true)
    },
    close_suggestion_menu: async function (query_str) {
      this.query_menu_open = false;
    },
    load_more_files: async function () {
      this.metadata.page += 1;
      await this.fetch_file_list(false)
    },
    update_compare_to_model_runs: function (value) {
      this.compare_to_model_run_list = value
    },
    update_base_model_run: function (value) {
      this.base_model_run = value
    },
    reset_file_thumbnails: function(file_list){
      for (let file of file_list){
        if(!file.image){
          continue
        }
        file.image.url_signed = null
      }
    },
    fetch_single_file_signed_url: async function(file, project_string_id){
      if(!file){
        return
      }
      let [url_data, err] = await get_file_signed_url(project_string_id, file.id);
      if (err){
        this.error = this.$route_api_errors(err)
      }
      let new_file_data = url_data.file
      if(new_file_data.type === 'sensor_fusion'){
        file.point_cloud = new_file_data.point_cloud
      }
      else{
        file[new_file_data.type] = new_file_data[new_file_data.type]
      }
    },
    fetch_file_thumbnails: function(file_list){
      for (let file of file_list){
        this.fetch_single_file_signed_url(file, this.$props.project_string_id)
      }
    },
    fetch_file_list: async function (reload_all = true) {
      if(reload_all){
        this.metadata.page = 1;
        this.loading = true
      }
      else{
        this.infinite_scroll_loading = true;
      }
      try{
        this.query_error = {}
        this.none_found = undefined
        if (this.cancel_request){
          this.cancel_request.cancel()
        }
        this.metadata.regen_url = false
        this.cancel_request = axios.CancelToken.source();
        const response = await axios.post('/api/project/' + String(this.$props.project_string_id) +
          '/user/' + this.$store.state.user.current.username + '/file/list', {
          'metadata': {
            ...this.metadata,
            query: this.query,
            previous: this.metadata_previous
          },
          'project_string_id': this.$props.project_string_id
        }, {  cancelToken: this.cancel_request.token,})
        if (response.data['file_list'] == false) {
          this.none_found = true
          this.file_list = this.metadata.page === 1 ? [] : this.file_list
        }
        else {
          this.reset_file_selected()
          this.reset_file_thumbnails(response.data.file_list)
          this.fetch_file_thumbnails(response.data.file_list)
          if(reload_all){
            this.file_list = response.data.file_list;
          }
          else{
            // TODO clarify point of this block relative to concat
            for(const file in response.data.file_list){
              if(!this.file_list.find(f => f.id === file.id)){
                this.file_list.push(file);
              }
            }
            this.file_list = this.file_list.concat(response.data.file_list);
            this.file_list = this.file_list.filter((file) => typeof file === 'object')
          }
        }
        this.metadata_previous = response.data.metadata;
        if(response.data.metadata.file_count){
          this.file_count = response.data.metadata.file_count;
        }

      }
      catch (error) {
        if (error.toString() !== 'Cancel'){
          console.error(error)
          this.query_error = this.$route_api_errors(error)
        }
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
    fetch_model_run_list: async function () {
      this.loading_models = true
      try {
        const response = await axios.post(
          `/api/v1/project/${this.$props.project_string_id}/model-runs/list`,
          {}
        );
        if (response.data['model_run_list'] != undefined) {
          this.model_run_list = response.data.model_run_list;
        }
      } catch (error) {
        console.error(error);
      } finally {
        this.loading_models = false;
      }

    },
    reset_file_selected: function(){
      for (let file_elm of this.file_list) {
        if (typeof file_elm === 'object') {
          file_elm.selected = false;
        }
      }
      this.selected_files = []
    },
    on_file_selected: function (file) {
      if(this.ctrl_key){
        file.selected = !file.selected;
        if(!this.selected_files.includes(file)){
          this.selected_files.push(file)
        } else if(!file.selected){
          this.selected_files = this.selected_files.filter(elm => elm.id !== file.id)
        }
      }
      else{
        this.reset_file_selected()
        file.selected = !file.selected;
        if(!this.selected_files.includes(file)){
          this.selected_files.push(file)
        }
      }

      this.$forceUpdate()
    },
    view_detail: function (file, model_runs, color_list) {
      this.$emit('view_detail', file, model_runs, color_list)
    },
    change_schema: function (e) {
      this.label_schema = e
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
