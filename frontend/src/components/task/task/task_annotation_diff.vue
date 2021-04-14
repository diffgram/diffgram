<template>
  <div v-cloak>

      <v_annotation_core  :view_only_mode_prop="true"
                          :render_mode=" 'file_diff' "
                          :is_annotation_assignment_bool="false"
                          :project_string_id="project_string_id"
                          :file_view_mode="'changes'"
                          :accesskey="'task_file_diff'"
                          :task_id_prop="task_id_prop"
                          :task_mode_prop="task_mode_data"
                          @file_list_length="file_length = $event">
      </v_annotation_core>
    

  </div>
</template>

<script lang="ts">

  import axios from 'axios';

  import Vue from "vue"; export default Vue.extend( {
    name: 'task_file_diff',
    props: [
      'task_id_prop',   // TODO clarify task mode prop vs task mode data
      'task_mode_data'
    ],
    data() {
      return {

        file_length: null

      }
    },
    computed: {

    },
    created() {



    },
    methods: {

     
    }
  }

) </script>
