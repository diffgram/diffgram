<template>
  <v-container fluid class="pt-0">

  </v-container>
</template>

<script lang="ts">
import Vue from "vue";
import axios from '../../services/customInstance';

export default Vue.extend({

    name: 'action_config',
    components: {

    },
    props: ['action', 'project_string_id', 'actions_list', 'steps_config'],

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
    },
    methods: {

    }
  }
) </script>


<style>
code{
  width: 100%;
  height: 100% !important;
}
</style>
