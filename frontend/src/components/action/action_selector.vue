<template>

  <div class="pr-6 pl-6" style="min-height: 850px">
    <v_error_multiple :error="error"></v_error_multiple>
    <v-text-field label="Search for an action..." v-model="search"></v-text-field>

    <v-container fluid class="d-flex flex-wrap" v-if="!loading">
      <action_step_box v-for="action in actions_list_filtered"
                       @add_action_to_workflow="add_action_to_workflow(action)"
                       style="width: 250px; height: 250px"
                       :icon="action.icon"
                       :name="action.name"
                       :description="action.description"
                       :is_trigger="action.is_trigger"
      >

      </action_step_box>
    </v-container>
    <v-container v-else>
      <v-progress-linear indeterminate></v-progress-linear>
    </v-container>
  </div>

</template>

<script lang="ts">
import Vue from "vue";
import axios from '../../services/customInstance';
import action_step_box from "./action_step_box.vue";
import {Action} from "./Action";
import {action_template_list} from './../../services/workflowServices';
export default Vue.extend({

    name: 'action_config_dialog',
    components: {
      action_step_box

    },
    props: ['action', 'project_string_id'],

    async mounted() {
      await this.api_action_template_list()
    },

    data() {
      return {
        is_open: false,
        loading: false,
        search: '',
        error: null,
        actions_template_list: [],
        actions_list: [
          new Action(
            'Human Labeling Task',
            'mdi-brush',
            'create_task',
            {
              trigger_event_name: 'file_uploaded',
              upload_directory_id_list: null,
              trigger_action_id: null,
            },
            {event_name: null},
            'Add tasks to a task template',
            {event_name: 'task_completed'}
          ),
          new Action(
            'JSON Export',
            'mdi-database-export-outline',
            'export',
            {
              trigger_event_name: 'task_completed',
              upload_directory_id_list: null,
              trigger_action_id: null,
            },
            {event_name: 'all_tasks_completed'},
            'Create JSON export from labeled data.',
            {event_name: 'export_generate_success'}
          )
        ],
      }
    },
    watch: {

    },
    computed: {
      actions_list_filtered: function(){
        if(!this.search || this.search === ''){
          return this.actions_template_list
        }
        return this.actions_template_list.filter(elm => elm.title.toLowerCase().includes(this.search.toLowerCase()))
      }
    },
    methods: {
      build_actions_list: function(action_template_list){
        this.actions_template_list = [];
        for(let template of action_template_list){
          let action = new Action(
            template.public_name,
            template.icon,
            template.kind,
            template.trigger_data,
            template.condition_data,
            template.description,
            template.completion_condition_data
          )
          action.id = template.id
          this.actions_template_list.push(action)
        }
      },
      api_action_template_list: async function(){

        let [result, err] = await action_template_list(this.project_string_id)
        if(err){
          this.error = this.$route_api_errors(err);
          return
        }
        if(result){
          this.build_actions_list(result.action_template_list)
        }

      },
      add_action_to_workflow: function(act){
        this.$emit('add_action_to_workflow', act)
        this.close();
      },
      close() {
        this.input = undefined;
        this.is_open = false;
      },
      open() {
        this.is_open = true;
      },
    }
  }
) </script>


<style>
code{
  width: 100%;
  height: 100% !important;
}
</style>
