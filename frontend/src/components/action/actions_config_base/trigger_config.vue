<template>
  <div class="mb-4">
    <h2 class="font-weight-light mr-6">1. Trigger When: </h2>
    <v-select item-text="name" item-value="value" :items="triggers_list" v-model="action.trigger_data.trigger_event_name"></v-select>
    <v_directory_list
      v-model="action.trigger_data.upload_directory_id_list"
      v-if="action.trigger_data.trigger_event_name === 'file_uploaded'"
      :project_string_id="project_string_id"
      :show_new="true"
      :show_update="true"
      @change_directory="">
    </v_directory_list>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
export default Vue.extend({
    name: 'trigger_config',
    props: ['action', 'project_string_id', 'actions_list', 'triggers_list_prop'],

    mounted() {

    },

    data() {
      return {
        is_open: true,
        search: '',
        default_triggers_list: [
          {
            name: 'File is uploaded',
            value: 'file_uploaded'
          },
          {
            name: 'Previous Step Completed',
            value: 'action_completed'
          },
        ],

      }
    },
    watch: {

    },
    computed: {
      triggers_list: function(){
        if(this.triggers_list_prop){
          return this.triggers_list_prop;

        }

        return this.default_triggers_list.filter( elm => {
          if(elm.value === 'action_completed' && !this.prev_action){
            return false
          }
          return true
        })
      },
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
