<template>
<div id="">

<v-card elevation="0">
  <v-container>
    <v-layout column>

      <v-card-title>
        Update Dataset
      </v-card-title>

      <v-text-field label="Name"
                    v-model="current_directory.nickname">
      </v-text-field>

      <v-btn @click="update_directory_api('RENAME')"
              :loading="loading"
              :disabled="loading"
              color="primary">
        Rename
      </v-btn>

      <v-btn @click="update_directory_api('ARCHIVE')"
              :loading="loading"
              :disabled="loading"
              color="warning">
        Archive
      </v-btn>

      <v_error_multiple :error="error">
      </v_error_multiple>

      <v-alert type="success"
                v-if="show_success">

        Success
      </v-alert>


      <!-- TODO option to clear / create another one? -->

    </v-layout>
  </v-container>

</v-card>

</div>
</template>

<script lang="ts">

import axios from '../../services/customAxiosInstance';


import Vue from "vue"; export default Vue.extend( {
  name: 'directory_update',
  props: [
    'project_string_id',
    'current_directory_prop'
    ],

  data() {
    return {

      mode: "RENAME",
      loading: false,
      error: {},
      show_success: false,

      current_directory: {
        nickname: ""
       }

    }
  },
  watch: {
    current_directory_prop() {
        this.current_directory = this.current_directory_prop
    }
  },
  mounted() {
    this.current_directory = this.current_directory_prop
  },
  computed: {

  },
  methods: {

    update_directory_api: function (mode) {

      this.mode = mode

      this.loading = true
      this.error = { }
      this.show_success = false

      // because of side effect of updating directory_list
      // ensures we are geting the correct one
      let cached_dir_id = this.current_directory.directory_id

      axios.post(
        '/api/v1/project/' + this.project_string_id
      + '/directory/update',
        {
          nickname: this.current_directory.nickname,

          directory_id: this.current_directory.directory_id,
          mode: this.mode

        }).then(response => {

          if (response.data.log.success == true) {

            this.show_success = true

            // We need to both update the directory list (side effect of project update)
            this.$store.commit('set_current_directory_list', response.data['project'].directory_list)

            // And set the current one
            // Why we update: It's not just because `set_project` has a side effect
            // of replacing directory, we also want the current one to match new information
            if (response.data.project && response.data.project.directory_list) {
              let updated_directory = response.data.project.directory_list.find(
                directory => {return directory.directory_id == cached_dir_id})
              if (updated_directory) {
                this.$store.commit('set_current_directory', updated_directory)
              } else {
                throw new Error("Could not find directory just updated.")
              }
            }

            if (this.mode == "ARCHIVE") {
              this.$store.commit('init_media_refresh')
            }

            this.loading = false

          }

        }).catch(error => {

          this.$route_api_errors(error)

          this.loading = false
          console.log(error)
        });

    }

  }
}
) </script>
