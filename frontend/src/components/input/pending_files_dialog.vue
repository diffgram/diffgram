<template>

  <v-dialog v-model="is_open" max-width="1500px" id="task-input-list-dialog">
    <v-card elevation="0">
      <input_view
        :project_string_id="project_string_id"
        :filters="filters"
        :show_status_filter="true"
        :initial_status_filter="'Processing'"
        :request_refresh="refresh_table"

      ></input_view>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import input_view from './input_view'
import axios from 'axios';
import Vue from "vue";

export default Vue.extend( {
  name: 'pending_files_dialog',
  components:{
    input_view
  },
  props: {
    'project_string_id': {
      default: null
    },

  },

  data() {

    return {
      filters:{
        mode: ['file_copy'],
        status: 'pending'
      },
      refresh_table: new Date(),
      is_open: false,
    }


  },
  computed: {

  },
  watch: {
    is_open: function(){
      this.refresh_table = new Date();
    }
  },
  mounted() {},

  beforeDestroy() {

  },

  methods: {
    async open() {
      this.is_open = true;
    }
  }
}
) </script>

