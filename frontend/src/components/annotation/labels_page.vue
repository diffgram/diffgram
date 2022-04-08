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

        <v-card>
        <div class="d-flex flex-column">
          <div class="pa-4 d-flex align-center justify-start ">
            <h1 class="font-weight-light mr-2"  >
              <v-icon v-if="!edit_name" color="secondary">mdi-group</v-icon>
              <span class="secondary--text" v-if="current_schema && !edit_name">{{current_schema.name}}</span>
              <span class="secondary--text" v-else-if="!current_schema && !edit_name">All Schemas</span>
            </h1>
            <tooltip_button
              v-if="!edit_name"
              tooltip_message="Change Name"
              @click="edit_name = true"
              icon="mdi-pencil"
              :icon_style="true"
              small
              color="primary"
              datacy="archive_schema_button"
            >
            </tooltip_button>
            <v-text-field
              v-if="edit_name"
              v-model="current_schema.name"
              @input="has_changes = true"
              @keyup.enter="update_schema_name"
              solo
              flat
              style="font-size: 22pt; border: 1px solid grey; height: 55px; max-width: 450px"
              color="blue"
            >
            </v-text-field>

            <div>
              <tooltip_button
                v-if="edit_name == true"
                @click="update_schema_name"
                color="primary"
                icon="save"
                :icon_style="true"
                tooltip_message="Save Name Updates"
                confirm_message="Confirm"
                :loading="loading"
                :disabled="loading || !has_changes"
              >
              </tooltip_button>
            </div>

            <tooltip_button
              v-if="edit_name == true"
              tooltip_message="Cancel Name Edit"
              datacy="cancel_edit_name"
              @click="edit_name = false"
              icon="mdi-cancel"
              :icon_style="true"
              color="primary"
              :disabled="loading"
            >
            </tooltip_button>



            <v-spacer></v-spacer>
            <button_with_confirm
              tooltip_message="Archive Schema"
              button_message="Archive Schema"
              @confirm_click="archive_schema"
              icon="mdi-delete"
              small
              button_color="error"
              :icon_style="true"
              datacy="archive_schema_button"
            >
            </button_with_confirm>
          </div>
          <v-tabs v-model="tab" color="secondary" style="height: 100%; width: 850px" >
            <v-tab class="pb-4 d-flex justify-start"
                   v-for="item in header_items" :key="item.text"
                   style="border: 1px solid #e0e0e0; border-bottom: none; width: 100%">
              <v-icon left>{{ item.icon }}</v-icon>
              {{ item.name }}
            </v-tab>
            <v-tabs-items v-model="tab">
              <v-tab-item>
                <v_labels_view
                  v-if="current_schema"
                  :schema_id="current_schema ? current_schema.id : undefined"
                  :show_edit_templates="true"
                  :show_create_samples="true"
                  :show_attributes_table="true"
                  :project_string_id="project_string_id">
                </v_labels_view>
              </v-tab-item>

              <v-tab-item>
                <attribute_home v-if="current_schema"
                                :schema_id="current_schema ? current_schema.id : undefined"
                                :project_string_id="project_string_id">

                </attribute_home>
              </v-tab-item>

              <v-tab-item>
                <instance_template_list
                  v-if="current_schema"
                  :schema_id="current_schema ? current_schema.id : undefined"
                  :project_string_id="project_string_id"
                ></instance_template_list>
              </v-tab-item>
            </v-tabs-items>
          </v-tabs>
        </div>
        </v-card>
      </div>
    </v-container>
  </div>

</template>

<script lang="ts">

import Vue from "vue";
import attribute_home from '../attribute/attribute_home'
import {create_event} from "../event/create_event";
import schema_card_selector from './schema_card_selector'
import instance_template_list from '../instance_templates/instance_template_list'
import {get_schemas, update_schema} from '../../services/labelServices'

export default Vue.extend({
  name: 'labels_page',
  components:{
    instance_template_list: instance_template_list,
    schema_card_selector: schema_card_selector,
    attribute_home: attribute_home
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
      header_items: [{name: 'Labels', icon: 'mdi-group'},
        {name: 'Attributes', icon: 'mdi-group'},
        {name: 'Label Templates', icon: 'mdi-group'}]
    }
  },
  computed: {},
  async mounted() {
    this.add_visit_history_event();
    await this.fetch_schemas();

  },
  async created() {


  },
  methods: {
    archive_schema: async function(){
      if(this.label_schema_list.length === 1){
        this.error = {schema: 'You must have at least 1 schema'}
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
        this.$refs.schema_selector.select_schema(this.label_schema_list[0]);
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
