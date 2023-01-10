<template>
  <div>

    <v-container class="d-flex flex-column">
      <v_error_multiple :error="error"></v_error_multiple>



      <div class="d-flex pt-8">
        <schema_card_selector
          :project_string_id="project_string_id"
          @schema_selected="on_schema_selected"
          @schema_created="on_schema_created"
          ref="schema_selector"
          :schema_list="label_schema_list">
        </schema_card_selector>

        <div style="width: 70%" class="d-flex flex-column">
          <div class="pa-4 d-flex align-center justify-start ">
            <h1 class="font-weight-light"  >
              <span class="secondary--text" v-if="!loading && current_schema && !edit_name">
                {{current_schema.name | truncate(45)}}
              </span>
            </h1>
            <standard_button
              v-if="!edit_name"
              tooltip_message="Change Name"
              @click="edit_name = true"
              icon="mdi-pencil"
              :icon_style="true"
              small
              :disabled="loading"
              color="primary"
              datacy="edit_schema_name_button"
            >
            </standard_button>

            <v-text-field
              data-cy="schema_name_text_field"
              v-if="!loading && current_schema && edit_name"
              v-model="current_schema.name"
              @input="has_changes = true"
              @keyup.enter="update_schema_name"
              :disabled="loading"
              solo
              flat
              style="font-size: 22pt; border: 1px solid grey; height: 55px; max-width: 450px"
              color="blue"
            >
            </v-text-field>

            <div>
              <standard_button
                v-if="edit_name == true"
                @click="update_schema_name"
                color="primary"
                icon="save"
                :icon_style="true"
                datacy="save_name_button"
                tooltip_message="Save Name Updates"
                confirm_message="Confirm"
                :loading="loading"
                :disabled="loading || !has_changes"
              >
              </standard_button>
            </div>

            <standard_button
              v-if="edit_name == true"
              tooltip_message="Cancel Name Edit"
              datacy="cancel_edit_name"
              @click="edit_name = false"
              icon="mdi-cancel"
              :icon_style="true"
              color="primary"
              :disabled="loading"
            >
            </standard_button>



            <v-spacer></v-spacer>
            <button_with_confirm
              tooltip_message="Archive Schema"
              button_message="Archive Schema"
              @confirm_click="archive_schema"
              icon="mdi-delete"
              :disabled="loading && !current_schema"
              small
              button_color="error"
              :icon_style="true"
              datacy_confirm="archive_schema_button_confirm"
              datacy="archive_schema_button"
            >
            </button_with_confirm>
          </div>
          <labels_manager_tabs :current_schema="current_schema" :project_string_id="project_string_id">

          </labels_manager_tabs>
        </div>
      </div>
    </v-container>
  </div>

</template>

<script lang="ts">

import Vue from "vue";

import {create_event} from "../../event/create_event";
import schema_card_selector from './schema_card_selector.vue'

import {get_schemas, update_schema} from '../../../services/labelServices'
import Labels_manager_tabs from "../../label/labels_manager_tabs.vue";

export default Vue.extend({
  name: 'labels_page',
  components:{
    Labels_manager_tabs,
    schema_card_selector: schema_card_selector,
  },
  props: {
    'project_string_id': {},
  },
  data() {
    return {
      current_schema: null,
      edit_name: false,
      schema_name: '',
      loading: false,
      has_changes: false,
      tab: null,
      error: null,
      label_schema_list: [],

    }
  },
  computed: {},
  async mounted() {
    this.add_visit_history_event();
    await this.fetch_schemas();

  },
  async created() {


  },
  filters:{
    truncate: function (value, numchars) {
      return value && value.length > numchars ? value.substring(0, numchars) + "..." : value
    },
  },
  methods: {
    archive_schema: async function(){
      if(this.label_schema_list.length === 1){
        this.error = {schema: 'You must have at least 1 schema'}
        return
      }
      this.current_schema.archived = true;
      let success = await this.api_update_schema(this.current_schema)
      if(success && this.current_schema.archived){
        this.label_schema_list = this.label_schema_list.filter(elm => elm.id !== this.current_schema.id);
        this.$refs.schema_selector.select_schema(this.label_schema_list[0]);
      }
    },
    update_schema_name: async function(){
      await this.api_update_schema(this.current_schema)

    },
    api_update_schema: async function(schema){
      let [result, error] = await update_schema(this.project_string_id, schema);
      if(error){
        this.error = this.$route_api_errors(error)
        return
      }
      if(result){
        this.current_schema = result;
        for(let i = 0; i < this.label_schema_list.length; i++){
          let current = this.label_schema_list[i]
          if(current.id === this.current_schema.id){
            Vue.set(this.label_schema_list, i, this.current_schema);
          }
        }
        this.edit_name = false;
        return true
      }
    },
    on_schema_created: function(new_schema){
      this.label_schema_list.push(new_schema)
      this.$refs.schema_selector.select_schema(new_schema);
    },
    on_schema_selected: function(schema){
      this.current_schema = schema;
    },
    fetch_schemas: async function(){
      let [result, error] = await get_schemas(this.project_string_id);
      if(error){
        this.error = this.$route_api_errors(error)
      }
      if(result){
        this.label_schema_list = result;
        if(!this.$route || !this.$route.query.schema_id){
          this.$refs.schema_selector.select_schema(this.label_schema_list[0]);
        }
        else{
          let schema_id_route = parseInt(this.$route.query.schema_id, 10)
          let schema = this.label_schema_list.find(elm => elm.id === schema_id_route)
          if(schema){
            this.$refs.schema_selector.select_schema(schema);
          }

        }

      }
    },
    add_visit_history_event: async function(){
      let page_name = 'label_templates'
      const event_data = await create_event(this.$props.project_string_id, {
        file_id: this.$props.file_id_prop,
        task_id: this.$props.task_id_prop,
        page_name: page_name,
        object_type: 'page',
        user_visit: 'user_visit',
      })
    },
  }
}
) </script>
