<template>
  <div id="">

    <v-card>
      <v-container>

        <v-layout column>

          <!-- LIST -->
          <v_credential_list :job_id="job_id"
                             :mode_options="'job_edit'"
                             :mode_view="'list'">
          </v_credential_list>
          <!-- LIST -->

        </v-layout>
      </v-container>

    </v-card>

  </div>
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
