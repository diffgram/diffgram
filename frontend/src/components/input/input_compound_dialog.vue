<template>

  <v-dialog v-model="is_open" id="input_payload" :click:outside="close">
    <v-card elevation="1">
      <v-card-title>Compound File:</v-card-title>
      <v-card-text>
          <input_view
            v-if="selected_input"
            :media_type="'compound'"
            :project_string_id="project_string_id"
            :compound_file_id="selected_input.file_id">

          </input_view>
      </v-card-text>
    </v-card>
  </v-dialog>

</template>

<script lang="ts">

import axios from '../../services/customInstance';
import input_view from './input_view.vue'
import Vue from "vue";
export default Vue.extend({

    name: 'input_payload_dialog',
    components: {
      input_view: input_view,
    },
    props: ['project_string_id', 'selected_input'],

    mounted() {

    },

    data() {
      return {
        loading: false,
        is_open: false,
        input: undefined
      }
    },
    watch: {

    },
    filters: {
      pretty: function (value) {
        return JSON.stringify(JSON.parse(value), null, 2);
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
