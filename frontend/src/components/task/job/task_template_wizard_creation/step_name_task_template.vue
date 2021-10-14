<template>
  <v-container>
    <h1 class="font-weight-medium text--primary">New Task Template Creation</h1>
    <p class="font-weight-medium text--primary">
      The following steps will guide you on the creation of a new task template
    </p>

    <h2 class="font-weight-medium text--primary">Task Template Name</h2>
    <v-text-field label="Name"
                  data-cy="name-input"
                  v-model="job.name">
    </v-text-field>
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

        }
      },
      created() {

      },

      computed: {

      },
      methods: {

      }
    }
  ) </script>
