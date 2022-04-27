<template>

  <v-container fluid>
    <create_task_action_config v-if="action.kind === 'create_task'" :project_string_id="project_string_id" :action="action"></create_task_action_config>
    <export_action_config v-if="action.kind === 'export'"
                          :prev_action="prev_action"
                          :project_string_id="project_string_id"
                          :action="action">

    </export_action_config>
  </v-container>
</template>

<script lang="ts">
import Vue from "vue";
import axios from '../../services/customInstance';
import action_step_box from "./action_step_box.vue";
import create_task_action_config from "./action_configurations/create_task_action_config";
import export_action_config from "./action_configurations/export_action_config";
export default Vue.extend({

    name: 'action_config',
    components: {
      action_step_box,
      create_task_action_config,
      export_action_config,

    },
    props: ['action', 'project_string_id', 'actions_list'],

    mounted() {

    },

    data() {
      return {
        is_open: true,
        search: '',

      }
    },
    watch: {

    },
    computed: {
      prev_action: function(){
        if(!this.actions_list){
          return
        }
        for(let i = 0; i < this.actions_list.length; i++){
          let current = this.actions_list[i]
          if(current === this.action){
            if(i === 0){
              return undefined
            }
            return this.actions_list[i- 1]
          }
        }
      },
      actions_list_filtered: function(){
        if(!this.search || this.search === ''){
          return this.actions_list
        }
        return this.actions_list.filter(elm => elm.node.title.includes(this.search))
      }
    },
    methods: {
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
