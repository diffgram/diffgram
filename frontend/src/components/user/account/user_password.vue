<template>
  <div v-cloak>
    <v-flex xs6 center>
      <v-card>

        <v-card-title>
          <h3 class="headline">Set a password</h3>
        </v-card-title>

        <v-container>

          <v_error_multiple :error="error">
          </v_error_multiple>
          <v-alert type="success"
                   :value="success">
            Set.
          </v-alert>

          <v-text-field :append-icon="password_hide ? 'visibility' : 'visibility_off'"
                        @click:append="() => (password_hide = !password_hide)"
                        :type="password_hide ? 'password' : 'text'"
                        label="Password"
                        data-cy="password1"
                        validate-on-blur
                        :rules="[rules.password]"
                        v-model="password">
          </v-text-field>

          <v-text-field :append-icon="password_hide_check ? 'visibility' : 'visibility_off'"
                        @click:append="() => (password_hide_check = !password_hide_check)"
                        :type="password_hide_check ? 'password' : 'text'"
                        label="Retype Password"
                        validate-on-blur
                        data-cy="password2"
                        :rules="[rules.password_check]"
                        v-model="password_check">
          </v-text-field>


          <v-btn color="primary"
                 data-cy="save_password_button"
                 :loading="loading"
                 @click="password_set"
                 :disabled="loading">
            Set
          </v-btn>
        </v-container>

      </v-card>
    </v-flex>
  </div>
</template>

<script lang="ts">
// @ts-nocheck
// get typescript to work with the "rules" dict
// for veutify

import axios from 'axios';

import Vue from "vue"; export default Vue.extend( {
  name: 'user_password',
  data() {
    return {
      loading: false,

      error: {},

      success: false,
      password: null as String,
      password_hide: true,

      password_check: null as String,
      password_hide_check: true,

      rules: {
        password: (value) => {
          const pattern = /^.{8,200}$/
          if (!pattern.test(value)) {
            return '8 to 200 characters'
          }
          return true
        },
        password_check: (value) => {

          // Run equals check first
          if (this.password != this.password_check) {
            return "Passwords must match"
          }

          // Don't need to rerun password check
          // since if they equal, and the first password as checked
          // then all clear
          return true
        }
      }
    }
  },
  methods: {
    password_set: function () {

      this.loading = true;
      this.error = {}
      this.success = false

      axios.post('/api/v1/user/password/set', {

        'password': this.password,
        'password_check': this.password_check

      }).then(response => {

        this.success = true
        this.password = null
        this.password_check = null
        this.loading = false
        let initial_setup = this.$route.query.initial_setup;
        if(initial_setup === 'true'){
          this.$router.push('/a/project/new?builder_api_enabled_success=true')
        }

      })
      .catch(error => {

        if (error.response.status == 400) {
          this.error = error.response.data.log.error
        }

        this.loading = false
      });
    },
  }
}

) </script>
