<template>

  <div style="height: 100%">
    <component :is="selected_action_config"
               :project_string_id="project_string_id"
               :actions_list="actions_list"
               :display_mode="display_mode"
               @action_updated="on_action_updated"
               @open_action_selector="$emit('open_action_selector')"
               :action="action"
    ></component>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import action_step_box from "./action_step_box.vue";
import create_task_action_config from "./action_configurations/create_task/create_task_action_config";
import img_properties_outliers_config from "./action_configurations/deepchecks/img_properties_outliers/img_properties_outliers_config";
import export_action_config from "./action_configurations/export/export_action_config";
import AzureTextAnalyticsSentimentAction from "./action_configurations/azure/AzureTextAnalyticsSentimentAction";


export const COMPONENTS_KIND_MAPPING = {
  'AzureTextAnalyticsSentimentAction': AzureTextAnalyticsSentimentAction,
  'export': export_action_config,
  'TaskTemplateActionRunner': create_task_action_config,
  'DeepcheckImagePropertyOutliers': img_properties_outliers_config
}


export default Vue.extend({

    name: 'action_config_factory',
    components: {
      action_step_box,
      create_task_action_config,
      export_action_config,
      AzureTextAnalyticsSentimentAction,
      img_properties_outliers_config

    },
    props: ['action', 'project_string_id', 'actions_list', 'display_mode'],

    mounted() {
      this.set_action_config_component()
    },

    data() {
      return {

        is_open: true,
        search: '',
        selected_action_config: null

      }
    },
    watch: {
      action:{
        deep: true,
        handler: function(){
          this.set_action_config_component()
        }
      }
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
      set_action_config_component: function(){
        this.selected_action_config = COMPONENTS_KIND_MAPPING[this.action.kind]
      },
      on_action_updated: function(act){
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
