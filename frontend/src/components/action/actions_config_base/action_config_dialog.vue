<template>
  <v-dialog v-model="is_open" max-width="1000px" id="action_config_dialog">
      <v-card>
        <v-card-title>Edit Step: </v-card-title>
        <v-card-text>
          <action_config_factory
            :action="action"
            :actions_list="actions_list"
            display_mode="form"
            :project_string_id="project_string_id"></action_config_factory>
        </v-card-text>

        <v-card-actions class="d-flex justify-end">
          <v-btn  large class="primary" @click="close">Close</v-btn>
          <v-btn large class="primary" color="success" @click="save_action">Save</v-btn>
        </v-card-actions>
      </v-card>
  </v-dialog>
</template>

<script lang="ts">
import Vue from "vue";
import action_config_form_base from './action_config_form_base';
import Action_config_factory from "../action_config_factory.vue";
export default Vue.extend({

    name: 'action_config_dialog',
    components: {
      Action_config_factory,
      action_config_form_base: action_config_form_base,
    },
    props: ['action', 'project_string_id', 'actions_list', 'steps_config_prop'],

    mounted() {

    },

    data() {
      return {
        is_open: false,
        search: '',

      }
    },
    watch: {

    },
    computed: {

    },
    methods: {
      open: function(){
        this.is_open = true
      },
      close: function(){
        this.is_open = false
      },
      save_action: function(){

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
