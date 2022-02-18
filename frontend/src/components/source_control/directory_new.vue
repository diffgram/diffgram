<template>
<div id="">

<v-card elevation="0">
  <v-container>
    <v-layout column>

      <v-card-title>
        New Dataset
      </v-card-title>

      <v-text-field label="Name"
                  v-model="nickname">
      </v-text-field>

      <v-btn @click="new_directory_api"
              :loading="loading"
              :disabled="loading"
              color="primary">
        Create
      </v-btn>

      <div class="text-xs-left pt-4">
      <v-btn color="primary"
              dark
              outlined
              href="https://diffgram.readme.io/docs/data-directories-introduction"
              target="_blank">
        Help
        <v-icon right>mdi-book</v-icon>
      </v-btn>
      </div>

      <v_error_multiple :error="error">
      </v_error_multiple>

      <v-alert type="success"
                v-if="show_success">
        Created.
      </v-alert>


      <!-- TODO option to clear / create another one? -->

    </v-layout>
  </v-container>

</v-card>

</div>
</template>

<script lang="ts">

import axios from '../../services/customAxiosInstance';
import sillyname from 'sillyname';

import Vue from "vue"; export default Vue.extend( {
  name: 'directory_new',
  props: ['project_string_id'],

  data() {
    return {

      mode: "user", // ["user", "diffgram", "..."]
      loading: false,
      error: {},
      show_success: false,

      nickname: sillyname().split(" ")[0],

    }
  },
  mounted() {
    if (!this.project_string_id) {
      this.project_string_id = this.$store.state.project.current.project_string_id
    }
  },
  computed: {

  },
  methods: {

    new_directory_api: function () {

      this.loading = true
      this.error = { }
      this.show_success = false

      axios.post(
        '/api/v1/project/' + this.project_string_id
      + '/directory/new',
        {
          nickname: this.nickname

        }).then(response => {

          if (response.data.log.success == true) {

            this.show_success = true

            //this.$store.commit('set_current_directory_list', response.data.project.directory_list);
            this.$store.commit('patch_single_directory', response.data.new_directory)

            this.$emit('directory_created', response.data.new_directory)

            this.loading = false

          }

        }).catch(error => {

          if (error.response.status == 400) {
            this.error = error.response.data.log.error
          }
          this.loading = false
          console.log(error)
        });

    }

  }
}
) </script>
