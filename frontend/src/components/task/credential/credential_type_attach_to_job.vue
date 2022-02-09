<template>


  <v-container fluid>

    <v-layout column>

      <!-- LIST -->
      <v_credential_list :job_id="job_id"
                         :mode_options="'job_edit'"
                         :allow_awards="allow_awards"
                         :mode_view="'list'">
      </v_credential_list>
      <!-- LIST -->

    </v-layout>
  </v-container>

</template>

<script lang="ts">

  import Vue from "vue"; export default Vue.extend( {
    name: 'credential_type_attach_to_job',
    props: {
      'project_string_id': {
        default: null
      },
      'job_id': {
        default: null
      },
      'allow_awards':{
        default: false
      }
    },
    data() {
      return {

        loading: false,

        guide_markdown: ""

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
