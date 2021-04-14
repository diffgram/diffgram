<template>
  <div v-cloak>


    <v-select :items="permission_level_list"
              v-model="permission_level"
              label="Select permission"
              item-value="text"
              :disabled="loading"
              prepend-icon="security"></v-select>

    <!--
        hide
        this until it provides more clear use.-->
    <!--
    Live or Test
    <v-switch v-model="is_live"
              :label="mode_text"
              :prepend-icon="mode_icon"
              >
    </v-switch>
    -->

    <v-btn color="primary"
           :loading="loading"
           @click.native="loader = 'loading'"
           @click="new_user"
           :disabled="loading">
      Generate
    </v-btn>


    <v-alert type="success" :value="result">
      {{result}}
    </v-alert>


    <div v-if="auth.client_id">

      Save these credentials in a secure place.
      The client secret cannot be displayed again.

      The example shown is in the format for easy copy
      and paste
      to get started with our SDK.
      For production we recommend storing it
      as an environment variable.

      <kbd
           style="font-size: 100%">
        project = Project(
            project_string_id = "{{project_string_id}}",
            client_id = "{{auth.client_id}}",
            client_secret = "{{auth.client_secret}}")                        
      </kbd>

    </div>



    <v_error_multiple :error="error">
    </v_error_multiple>


  </div>
</template>

<script lang="ts">

import axios from 'axios';

import Vue from "vue"; export default Vue.extend( {
  name: 'auth_api_new',
  props: ['project_string_id'],
  data() {
    return {
      loading: false,
      error: {},
      result: null,

      is_live: true,

      auth: {

      },
      show_auth: false,

      permission_level_list: ['Editor', 'Viewer'],
      permission_level: 'Editor',

    }
  },

  computed: {

      mode_text: function () {

        if (this.is_live == true) {
          return "Live"
        } else {
          return "Test"
        }
      },

      mode_icon: function () {

        if (this.is_live == true) {
          return "mdi-check-circle"
        } else {
          return "mdi-test-tube"
        }
      }
  },

  methods: {
    new_user: function () {

      this.loading = true
      this.error = {}
      this.result = null

      axios.post('/api/v1/project/' + this.project_string_id
               + '/auth/api/new',
      {
        'permission_level': this.permission_level,
        'is_live': this.is_live

      }).then(response => {

        this.result = "Success"
        this.loading = false

        this.$store.commit('auth_members_refresh')

        this.show_auth = true
        this.auth = response.data.auth

      })
      .catch(error => {
        this.loading = false

        if (error.response) {
          if (error.response.status == 400) {
            this.error = error.response.data.log.error
          }

          if (error.response.status == 429) {

            this.error.rate_limit = "Too many requests, please try again later."
          }
          if (error.response.status == 403) {

            // CAUTION must replace dict, if just do the key thing it doesn't seem to detect
            // change as expected.

            this.error = "Invalid permission."
          }
        }

      });
    }
  }
}

) </script>
