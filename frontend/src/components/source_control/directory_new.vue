<template>
  <div id="">

  <!-- A Vuetify card component with no elevation and a container inside it -->
  <v-card elevation="0">
    <v-container>
      <v-layout column>

        <!-- The title of the card -->
        <v-card-title>
          New Dataset
        </v-card-title>

        <!-- A Vuetify text field for the user to input a name for the new dataset -->
        <v-text-field label="Name"
                    v-model="nickname">
        </v-text-field>

        <!-- A Vuetify button that calls the `new_directory_api` method when clicked, and is disabled and shows a loading spinner when the `loading` data property is true -->
        <v-btn @click="new_directory_api"
                :loading="loading"
                :disabled="loading"
                color="primary">
          Create
        </v-btn>

        <!-- A div with some text and a Vuetify button that opens the Diffgram documentation in a new tab when clicked -->
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

        <!-- A Vue ErrorMultiple component that displays an error message if the `error` data property is not an empty object -->
        <v_error_multiple :error="error">
        </v_error_multiple>

        <!-- A Vuetify alert component that shows a success message if the `show_success` data property is true -->
        <v-alert type="success"
                  v-if="show_success">
          Created.
        </v-alert>

        <!-- A TODO comment -->
        <!-- TODO option to clear / create another one? -->

      </v-layout>
    </v-container>

  </v-card>

  </div>
</template>

<script lang="ts">

// Import the axios library for making HTTP requests
import axios from '../../services/customInstance';

// Import the sillyname library for generating random names
import sillyname from 'sillyname';

// Import Vue and extend the Vue class to create a new Vue component
import Vue from "vue"; export default Vue.extend( {
  name: 'directory_new',
  props: ['project_string_id'],

  // Define the data properties for the component
  data() {
    return {

      mode: "user", // The mode of the component, which can be "user", "diffgram", or something else
      loading: false, // A flag indicating whether the component is currently loading data
      error: {}, // An object to store any error messages
      show_success: false, // A flag indicating whether a success message should be shown

      nickname: sillyname().split(" ")[0], // The name of the new dataset

    }
  },
  // Run code when the component is mounted to the DOM
  mounted() {
    // If the `project_string_id` prop is not defined, set it to the current project's ID from the Vuex store
    if (!this.project_string_id) {
      this.project_string_id = this.$store.state.project.current.project_string_id
    }
  },
  computed: {

  },
  // Define the methods for the component
  methods: {

    // The `new_directory_api` method, which is called when the "Create" button is clicked
    new_directory_api: function () {

      // Set the `loading` flag to true
      this.loading = true
      // Reset the `error` object
      this.error = { }
      // Reset the `show_success` flag
      this.show_success = false

      // Make a POST request to the Diffgram API to create a new dataset
      axios.post(
        '/api/v1/project/' + this.project_string_id
      + '/directory/new',
        {
          // Send the `nickname` and `access_type` data properties as the request body
          nickname: this.nickname,
          access_type: 'project'

        }).then(response => {

          // If the request was successful, set the `show_success` flag to true
          // and update the Vuex store with the new dataset
          if (response.data.log.success == true) {

            this.show_success = true

            //this.$store.commit('set_current_directory_list', response.data.project.directory_list);
            this.$store.commit('patch_single_directory', response.data.new_directory)

            this.$emit('directory_created', response.data.new_directory)

            this.loading = false

          }

        }).catch(error => {

          // If the request failed, set the `error` object to the error response
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
