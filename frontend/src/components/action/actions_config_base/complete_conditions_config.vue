<template>

  <div class="mb-4">
    <h2 class="font-weight-light mr-6">4. Completes When: </h2>
    <v-select item-text="name" item-value="value" :items="completion_condition_list" v-model="action.completion_condition_data.event_name"></v-select>
  </div>

</template>

<script lang="ts">
import Vue from "vue";
import {Action} from "../Action";


export default Vue.extend({

    name: 'complete_conditions_config',
    components: {

    },
    props:{
      action:{
        required: true,
        type: Action
      },
      project_string_id:{
        required: true,
      },
      actions_list:{
        required: true,
      },
      completion_condition_list_prop:{
        required: false,
      }
    },
    mounted() {

    },

    data() {
      return {
        is_open: true,
        search: '',
        default_complete_condition_list: [
          {
            name: 'File is uploaded',
            value: 'file_uploaded'
          },
          {
            name: 'Task is completed',
            value: 'task_completed'
          },
          {
            name: 'Previous Step Completed',
            value: 'action_completed'
          },
        ],

      }
    },
    watch: {},
    computed: {
      completion_condition_list: function(){
        if(this.completion_condition_list_prop){
          return this.completion_condition_list_prop;
        }
        return this.default_complete_condition_list;
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
code {
  width: 100%;
  height: 100% !important;
}
</style>
