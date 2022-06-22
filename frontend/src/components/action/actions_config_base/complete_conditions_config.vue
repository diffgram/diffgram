<template>

  <div class="mb-4">
    <h3 class="mr-6">4. Completes When: </h3>
    <v-select item-text="name" item-value="value"
              :items="completion_condition_list"
              v-model="action.completion_condition_data.event_name"></v-select>
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
      },
      action_template:{
        required: true,
      }
    },
    mounted() {
      this.set_complete_condition_list(this.action_template)
    },

    data() {
      return {
        is_open: true,
        selected_condition: null,
        search: '',
        completion_condition_list: [],

      }
    },
    watch: {
      action_template: {
        deep: true,
        handler: function(new_val, old_val){
          this.set_complete_condition_list(new_val)
        }
      },
    },
    computed: {

    },
    methods: {
      set_complete_condition_list: function(action_template){
        if(!action_template){
          return
        }
        if(!action_template.completion_condition_data){
          return
        }
        if (action_template.completion_condition_data && action_template.completion_condition_data.event_list) {
          this.completion_condition_list = action_template.completion_condition_data.event_list
          let selected = this.completion_condition_list.find(elm => elm.value === action_template.completion_condition_data.default_event_name)
          if(selected){
            this.action.completion_condition_data.event_name = selected.value
          }
        }
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
code {
  width: 100%;
  height: 100% !important;
}
</style>
