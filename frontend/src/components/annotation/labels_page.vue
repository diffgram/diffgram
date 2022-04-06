<template>
  <div>
    <div class="pa-4 ml-12">
      <h1 class="mb-4 font-weight-light">Project/{{project_string_id}}/Schema/ <strong class="text--secondary" v-if="current_schema">{{current_schema.name}}</strong></h1>
    </div>
    <v-container class="d-flex flex-column">
      <v_error_multiple :error="error"></v_error_multiple>

      <div class="d-flex">
        <schema_card_selector :schema_list="label_schema_list">
        </schema_card_selector>
        <div class="d-flex flex-column">
          <div>
            <v_labels_view
              :show_edit_templates="true"
              :show_create_samples="true"
              :show_attributes_table="true"
              :project_string_id="project_string_id">
            </v_labels_view>

          </div>
          <div>
            <instance_template_list

              :project_string_id="project_string_id"
            ></instance_template_list>
          </div>
        </div>
      </div>
    </v-container>
  </div>

</template>

<script lang="ts">

import Vue from "vue";
import {create_event} from "../event/create_event";
import schema_card_selector from './schema_card_selector'
import instance_template_list from '../instance_templates/instance_template_list'
import get_schemas from '../../services/labelServices'

export default Vue.extend({
  name: 'labels_page',
  components:{
    instance_template_list: instance_template_list,
    schema_card_selector: schema_card_selector
  },
  props: {
    'project_string_id': {},
  },
  data() {
    return {
      current_schema: null,
      error: null,
      label_schema_list: []
    }
  },
  computed: {},
  mounted() {
    this.add_visit_history_event();
  },
  async created() {
    await this.fetch_schemas();

  },
  methods: {
    fetch_schemas: async function(){
      let [result, error] = await get_schemas(this.project_string_id);
      if(error){
        this.error = this.$route_api_errors(error)
      }
      if(result){
        this.label_schema_list = result;
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
