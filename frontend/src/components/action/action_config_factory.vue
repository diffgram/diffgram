<template>

  <div style="height: 100%">
    <h2 class="font-weight-light font-weight-medium" v-if="action">{{action.ordinal + 1}}. {{action.public_name}}</h2>
    <component :is="selected_action_config"
               :project_string_id="project_string_id"
               :actions_list="actions_list"
               :display_mode="display_mode"
               :workflow="workflow"
               :action="action"
               @action_updated="on_action_updated"
               @open_action_selector="$emit('open_action_selector')"
    ></component>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import action_step_box from "./action_step_box.vue";
import COMPONENTS_KIND_MAPPING from "./component_mapping"


export default Vue.extend({
    name: 'action_config_factory',
    components: {
      action_step_box
    },
    props: ['action', 'project_string_id', 'actions_list', 'display_mode', 'workflow'],

    mounted() {
      console.log('MONTEEEEED', this.selected_action_config)
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
        console.log('SETTTT', this.selected_action_config)
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
