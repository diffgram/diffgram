<template>

  <div class="pr-6 pl-6" style="min-height: 850px">
    <v-text-field label="Search for an action..." v-model="search"></v-text-field>

    <v-container fluid class="d-flex flex-wrap">
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
  </div>

</template>

<script lang="ts">
import Vue from "vue";
import axios from '../../services/customInstance';
import action_step_box from "./action_step_box.vue";
import {Action} from "./Action";
export default Vue.extend({

    name: 'action_config_dialog',
    components: {
      action_step_box

    },
    props: ['action'],

    mounted() {

    },

    data() {
      return {
        is_open: false,
        search: '',
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
            {condition: null},
            'Add tasks to a task template',
            'task_completed'
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
            {condition: 'all_tasks_completed'},
            'Create JSON export from labeled data.',
            'export_generate_success'
          )
        ],
      }
    },
    watch: {

    },
    computed: {
      actions_list_filtered: function(){
        if(!this.search || this.search === ''){
          return this.actions_list
        }
        return this.actions_list.filter(elm => elm.title.toLowerCase().includes(this.search.toLowerCase()))
      }
    },
    methods: {

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
