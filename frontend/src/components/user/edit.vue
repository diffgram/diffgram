<template>
  <div v-cloak>

    <v-card>

      <v-card-title>
        <h3 class="headline">Welcome {{ $store.state.user.current.first_name }}</h3>
      </v-card-title>

      <v-container>
        <v-layout >

          <user_profile_image_edit>

          </user_profile_image_edit>

            <v-text-field label="Email"
                          data-cy="email-field"
                          v-model="email"
                          :disabled="true"
                          class="pl-4"
                          >
            </v-text-field>

        </v-layout>

        <v-layout>

          <v-flex >
            <v-text-field label="First name"
                          data-cy="first_name_field"
                          v-model="first_name">
            </v-text-field>
          </v-flex>
          <v-flex xs12 sm6>
            <v-text-field label="Last name"
                          data-cy="last_name_field"
                          v-model="last_name">
            </v-text-field>
          </v-flex>

        </v-layout>

        <v-layout>
          <v-flex>

            <!-- Hide for release-->
            <!--
<v-text-field label="Profile URL"
              v-model="profile_url">
</v-text-field>
-->

            <v-btn color="primary"
                   data-cy="save_edit"
                    :loading="loading"
                    @click="edit_user"
                    :disabled="loading">
              Save
            </v-btn>

            <v-btn color="primary"
                   data-cy="set_password_button"
                    :loading="loading"
                    @click="route_password_set"
                    :disabled="loading">
              Set Password
            </v-btn>

            <v-btn color="green"
                    dark
                   data-cy="2fa_button"
                    @click="route_2fa"
                    :disabled="loading">
              2 Factor Authentication
            </v-btn>

          </v-flex>

        </v-layout>

        <div v-if="$store.state.builder_or_trainer.mode =='builder'">
          <h2 class="pa-4"> Beta </h2>

          <div v-if="!$store.state.user.current.api.api_actions">
            <v-btn  color="blue darken-1"
                   dark
                   outlined
                    @click="api_user_update('api_actions')"
                    >
              <v-icon left>mdi-brain</v-icon>
                Enable Actions and Brains
            </v-btn>
           <v-icon right color="primary"> mdi-new-box </v-icon>
          </div>

          <v-alert :value="$store.state.user.current.api.api_actions"
                  type="success"
                  >
            Actions and Brains Enabled. See Action Menu on Header.
          </v-alert>
        </div>


      </v-container>

    </v-card>

  </div>
</template>

<script lang="ts">
// @ts-nocheck

import axios from '../../services/customInstance';

import Vue from "vue"; export default Vue.extend( {
  name: 'user_edit',
  data() {
    return {
      loading: false,

      api_user_update_loading : false,

      // TODO get email from current user
      email: this.$store.state.user.current.email,
      first_name: this.$store.state.user.current.first_name,
      last_name: this.$store.state.user.current.last_name,
      profile_url: null,

      error_list: [],

      rules: {
        required: (value) => !!value || 'Required.',
        email: (value) => {
          const pattern = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
          return pattern.test(value) || 'Invalid e-mail.'
        }
      }

    }
  },

  computed: {
    // could check if valid email when user clicks on next box...
    example_url: function () {
      if (this.url != null) {
        return "diffgram.com/u/" + this.url
      } else {
        return "diffgram.com/u/public_profile_url"
      }
    }
  },

  created() {

  },

  methods: {

    edit_user: function () {

      this.loading = true;

      axios.post('/api/user/edit', {
        user: {
          'email': this.email,
          'first_name': this.first_name,
          'last_name': this.last_name,
          'profile_url': this.profile_url
        }
      }).then(response => {

        if (response.data['success'] == true) {

          this.loading = false

          // Update user
          this.$store.commit('set_current_user',
                            response.data.user)

        } else {

        }

      })
      .catch(error => { this.loading = false
      });
    },
    route_2fa: function () {
      this.$router.push('/user/edit/2fa')
    },

    route_password_set: function () {
      this.$router.push('/user/account/password/set')

    },
    api_user_update(api_name) {

      this.api_user_update_loading = true
      this.info = {}  // reset

      axios.post('/api/v1/user/api/update',
        {
          'api_name': api_name
        })
        .then(response => {

          // update flags
          this.$store.commit('set_current_user', response.data.user)

          this.api_user_update_loading = false

        }).catch(e => {

          this.api_user_update_loading = false
          this.error_multiple = e.response.data.log.error
          console.error(e)

        })

      }
  }
}

) </script>
