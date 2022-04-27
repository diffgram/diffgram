<template>

  <v-dialog v-model="is_open" id="input_payload" :click:outside="close">
    <v-card class="pa-6" style="min-height: 850px">
      <v-card-text>
        <h1>Select An Action</h1>
        <v-text-field label="Search for an action..." v-model="search"></v-text-field>

        <v-container fluid class="d-flex flex-wrap">
          <action_step_box v-for="action in actions_list_filtered"
                           @add_action_to_workflow="add_action_to_workflow(action)"
                           style="width: 250px; height: 250px"
                           :icon="action.icon"
                           :title="action.title"
                           :description="action.description"
                           :is_trigger="action.is_trigger"
          >

          </action_step_box>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>

</template>

<script lang="ts">
import Vue from "vue";
import axios from '../../services/customInstance';
import action_step_box from "./action_step_box.vue";
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
          {
            is_trigger: true,
            icon: 'mdi-folder-arrow-up',
            kind: 'file_upload',
            title: 'On File Uploaded',
            description: 'When a file is uploaded',
          },
          {
            is_trigger: true,
            icon: 'mdi-brush',
            kind: 'create_task',
            title: 'Create Human Labeling Task',
            description: 'Add tasks to a task template',
          },
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
        return this.actions_list.filter(elm => elm.node.title.toLowerCase().includes(this.search.toLowerCase()))
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
