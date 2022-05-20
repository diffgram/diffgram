<template>

  <div>
    <create_task_action_config v-if="action.kind === 'create_task'"
                               :project_string_id="project_string_id"
                               :actions_list="actions_list"
                               :display_mode="display_mode"
                               @action_updated="on_action_updated"
                               :action="action">

    </create_task_action_config>
    <export_action_config v-if="action.kind === 'export'"
                          :prev_action="prev_action"
                          :display_mode="display_mode"
                          :actions_list="actions_list"
                          :project_string_id="project_string_id"
                          @action_updated="on_action_updated"
                          :action="action">

    </export_action_config>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import axios from '../../services/customInstance';
import action_step_box from "./action_step_box.vue";
import create_task_action_config from "./action_configurations/create_task/create_task_action_config";
import export_action_config from "./action_configurations/export/export_action_config";
export default Vue.extend({

    name: 'action_config_factory',
    components: {
      action_step_box,
      create_task_action_config,
      export_action_config,

    },
    props: ['action', 'project_string_id', 'actions_list', 'display_mode'],

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
      on_action_updated: function(act){
        console.log('on_action_updated FACT', act)
        this.$emit('action_updated', act)
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
