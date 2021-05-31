<template>
  <div v-cloak>

    <v-layout class="d-flex flex-row align-center" justify-start>
      <v-flex>
        <v-btn @click="add_dirs_to_job_api('update')"
               v-if="true"
               dark
               :loading="loading"
               class="ml-4"
               color="green">
          Update Datasets Attachments
          <v-icon right> mdi-attachment </v-icon>
        </v-btn>
      </v-flex>


      <div class="d-flex ml-6 justify-center align-center">
        <v-alert type="success"
                 dismissible
                 class="pt-1 pb-1 mb-0"
                 :value="show_success">

          Updated.
        </v-alert>
      </div>
    </v-layout>




    <v_error_multiple :error="error">
    </v_error_multiple>


  </div>
</template>

<script lang="ts">

  import axios from 'axios';

  import Vue from "vue"; export default Vue.extend( {
    name: 'dir_file_attach',
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


      add_dirs_to_job_api(add_or_remove) {

        this.add_or_remove = add_or_remove

        if (this.loading == true) {
          return
        }

        this.loading = true
        this.show_success = false
        this.error = {}

        axios.post(
            '/api/v1/project/' + this.project_string_id
          + '/job/dir/attach',
          {
            directory_list: this.selected,
            job_id: parseInt(this.job_id),
            add_or_remove: this.add_or_remove,
          })
          .then(response => {

            this.show_success = true

            this.loading = false

          })
          .catch(error => {
            if (error.response) {
              this.error = error.response.data.log.error
            }

            console.error(error);
            this.loading = false
          });

      }

    }
  }

) </script>
