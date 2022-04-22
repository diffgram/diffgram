<template>
  <v-container fluid id="" style="height: 100%;">

    <v-card style=" min-height: 800px">
      <v-card-title>Workflow Builder</v-card-title>
      <div class="d-flex">
        <v-card class="ml-2" width="30%" style=" min-height: 700px">
          <v-card-title>Steps: </v-card-title>
          <v-card-text>

          </v-card-text>


        </v-card>
      </div>

    </v-card>

  </v-container>
</template>

<script lang="ts">

  import axios from '../../services/customInstance';
  import action_existing_list from './action_existing_list.vue';
  import upload from '../upload_large.vue';
  import workflow_run_list from './workflow_run_list.vue';


  import Vue from "vue";

  export default Vue.extend({

      name: 'workflow_steps_visualizer',

      components: {

      },
      props: {
        'project_string_id': {
          default: null
        },
        'workflow': {
          default: null
        }
      },

      data() {
        return {
          loading: false,
          error: {},
        }
      },
      computed: {},
      methods: {


      }
    }
  ) </script>
