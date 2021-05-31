<template>
  <div v-cloak>

    <v-layout>
      <v-flex xs6>

        <v-btn @click="add_files_to_job_api('add')"
               v-if="true"
               dark
               :disabled="!files_available"
               :loading="loading"
               color="green">
          Attach
          <v-icon right> mdi-attachment </v-icon>
        </v-btn>

      </v-flex>
      <v-flex xs6>

        <v-btn @click="add_files_to_job_api('remove')"
               v-if="true"
               dark
               :disabled="!files_available"
               :loading="loading"
               color="orange">
          Remove
          <v-icon right> mdi-minus </v-icon>
        </v-btn>
      </v-flex>
    </v-layout>


    <v-alert type="success"
             dismissible
             v-if="show_success">

      Updated.
    </v-alert>

    <v_error_multiple :error="error">
    </v_error_multiple>


  </div>
</template>

<script lang="ts">

  import axios from 'axios';

  import Vue from "vue"; export default Vue.extend( {
    name: 'task_file_attach',
    props: [
      'project_string_id',
      'file_list',
      'selected',
      'job_id',
      'select_from_metadata',
      'metadata_previous'
    ],
    data() {
      return {
        loading: false,

        error: {},
        show_error: false,

        add_or_remove_list: ['Add', 'Remove'],
        add_or_remove: 'Add',

        show_success: false

      }
    },
    computed: {
      files_available: function () {
        if (this.file_list.length > 0) {
          return true
        }
        if (this.file_list.length == 0) {
          return false
        }
        return false
      }

    },
    created() {


    },
    methods: {


      add_files_to_job_api(add_or_remove) {

        this.add_or_remove = add_or_remove

        if (this.loading == true) {
          return
        }

        this.loading = true
        this.show_success = false
        this.error = {}

        axios.post(
            '/api/v1/project/' + this.project_string_id
          + '/job/file/attach',
          {
            file_list_selected: this.selected,
            job_id: parseInt(this.job_id),
            add_or_remove: this.add_or_remove,
            directory_id: this.$store.state.project.current_directory.directory_id,
            select_from_metadata: this.select_from_metadata,
            metadata_proposed: this.metadata_previous
          })
          .then(response => {

            this.show_success = true

            this.$store.commit('init_media_refresh')

            /* Context of updating counts for example
             * Component is like 4 deep from where we want
             * to show this so using vuex.
             */
            this.$store.commit('set_job', response.data.job)

            this.loading = false

          })
          .catch(error => {
            if (error.response) {
              this.error = error.response.data.log.error
            }
            // Still refresh it
            // Till we handle error messages better here
            this.$store.commit('init_media_refresh')

            console.error(error);
            this.loading = false
          });

      }

    }
  }

) </script>
