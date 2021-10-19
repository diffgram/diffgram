<template>
  <v-container fluid>
    <h1 class="font-weight-medium text--primary mb-8"><v-icon color="primary" class="mr-4" size="48">mdi-brush</v-icon>Task Template Creation</h1>
    <v_error_multiple :error="error"></v_error_multiple>
    <p class="text--primary">
      The following steps will guide you on the creation of a new task template
    </p>
    <h4>Give a name to your Task Template: </h4>
    <v-text-field label="Name"
                  data-cy="name-input"
                  v-model="job.name">
    </v-text-field>

    <v-container fluid class="mt-8 pa-0 d-flex justify-end" style="width: 100%">
<!--      <v-btn x-large color="primary" @click="$emit('previous_step')">Previous</v-btn>-->
      <v-btn x-large color="primary" @click="on_next_button_click">Next</v-btn>
    </v-container>
  </v-container>

</template>

<script lang="ts">

  import axios from 'axios';


  import Vue from "vue";

  export default Vue.extend({
      name: 'step_name_task_template',
      props: [
        'project_string_id',
        'job'
      ],

      components: {

      },

      data() {
        return {
          error: {}
        }
      },
      created() {

      },

      computed: {

      },
      methods: {
        verify_name: function(){
          if(!this.$props.job.name || this.$props.job.name === ''){
            this.error = {
              name: 'Name must not be empty.'
            }
            return false
          }
          return true
        },
        on_next_button_click: function(){
          this.error = {};
          let name_ok = this.verify_name();
          if(name_ok){
            this.$emit('next_step');
          }
        },

      }
    }
  ) </script>
