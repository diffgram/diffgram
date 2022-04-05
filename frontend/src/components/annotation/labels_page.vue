<template>
  <div class="d-flex flex-column pa-4">
    <h1 class="font-weight-light">Project/{{project_string_id}}/Schema/ <strong>{{current_schema.name}}</strong></h1>
    <schema_card_selector>

    </schema_card_selector>
    <v-container>
      <v_labels_view
          :show_edit_templates="true"
          :show_create_samples="true"
          :show_attributes_table="true"
          :project_string_id="project_string_id"
      >
      </v_labels_view>

    </v-container>
    <v-container>
      <instance_template_list

        :project_string_id="project_string_id"
      ></instance_template_list>
    </v-container>
  </div>
</template>

<script lang="ts">

import Vue from "vue";
import {create_event} from "../event/create_event";
import schema_card_selector from './schema_card_selector'
import instance_template_list from '../instance_templates/instance_template_list'
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
      label_schema_list: []
    }
  },
  computed: {},
  mounted() {
    this.add_visit_history_event();
  },
  created() {


  },
  methods: {
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
