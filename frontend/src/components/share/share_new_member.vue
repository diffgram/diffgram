<template>
  <div v-cloak>

    <v-card :elevation="elevation">
      <v-card-title v-if="show_sdk_share">

        <!--

         UI / user view CAUTION

         we have project and org permission scopes

          so want to be clear the user is sharing the PROJECT not the org

        -->
        <h3 class="headline" v-if="show_sdk_share">Share Project</h3>

        <v-spacer>
        </v-spacer>

        <!-- All this button does is toggle the member_kind
            instead of user having to "know" to do it in select.
            -->
         <v-btn v-if="member_kind == 'User' && show_sdk_share"
               color="primary"
               outlined
                :loading="loading"
                @click="member_kind = 'Developer Authentication (API/SDK)'"
                :disabled="loading">
            Developer Authentication (API/SDK)
        </v-btn>

      </v-card-title>

      <v-container>

        <v-alert type="error" :value="errors">
          {{errors}}
        </v-alert>

        <h2> <v-icon color="primary">mdi-plus</v-icon> Add members </h2>

        <v-select :items="member_kind_list"
                  v-model="member_kind"
                  label="Member type"
                  item-value="text"
                  :disabled="loading"
                  prepend-icon="mdi-security-account"></v-select>

        <div v-if="member_kind=='Developer Authentication (API/SDK)'">

          <auth_api_new :project_string_id="project_string_id"></auth_api_new>

        </div>
        <div v-else>
          <v-text-field label="Email"
                        v-model="email"
                        validate-on-blur
                        :rules="[rules.email]"
                        prepend-icon="email"
                        :disabled="loading">
          </v-text-field>

          <v-select :items="permission_type_list"
                    v-model="permission_type"
                    label="Select permission"
                    item-value="text"
                    :disabled="loading"
                    prepend-icon="security"></v-select>

          <v-layout>
            <v-text-field label="Optional: Include a personal message..."
                          v-model="note"
                          prepend-icon="note"
                          :disabled="loading">
            </v-text-field>

            <v-checkbox label="Notify"
                        v-model="notify">
            </v-checkbox>
          </v-layout>

          <v-btn color="primary"
                 :loading="loading"
                 @click.native="loader = 'loading'"
                 @click="new_user"
                 :disabled="loading">
            Invite
          </v-btn>

        </div>

      <v_error_multiple :error="error">
      </v_error_multiple>

      </v-container>

      <v-alert type="success" v-if="result">
        {{result}}
      </v-alert>
    </v-card>



  </div>
</template>

<script lang="ts">

import axios from 'axios'
import auth_api_new from '../auth/api/auth_api_new'


import Vue from "vue"; export default Vue.extend( {
  name: 'share_new',
  components: {
    auth_api_new
  },
  props:{
    'project_string_id':{
      default: null
    },
    'show_sdk_share':{
      default: true
    },
    'elevation':{
      default: 1
    }
  },
  data() {
    return {

      loading: false,
      email: null,
      errors: null,
      note: null,
      result: null,

      notify: true,

      error: {}, // new standard error

      // careful this is 'human' and 'api' on back end.
      member_kind_list: ['User', 'Developer Authentication (API/SDK)'],
      member_kind: 'User',

      permission_type_list: ['admin', 'Editor', 'Viewer'],
      permission_type: 'Editor',


      rules: {
        required: (value) => !!value || 'Required.',
        email: (value) => {
          const pattern = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
          return pattern.test(value) || 'Invalid e-mail.'
        }
      }

    }
  },
  methods: {
    new_user: function () {

      this.loading = true
      this.errors = null
      this.error = {}
      this.result = null

      axios.post('/api/project/' + this.project_string_id + '/share', {

        user_dict: {
          email: this.email,
          permission_type: this.permission_type,
          note: this.note
        },
        notify: this.notify,
        mode: 'NEW'


      }).then(response => {
        if (response.data['success'] == true) {

          // TODO add user to list?
          this.result = "Success"
          this.loading = false
          this.email = null
          this.note = null

          this.$store.commit('auth_members_refresh')
          this.$emit('member_invited')

        } else {
          this.errors = response.data['errors'],
          this.loading = false
        }
      })
      .catch(error => {
        this.loading = false

        // CAUTION these errors are for user only NOT auth API

         if (error.response) {
          if (error.response.status == 400) {
            this.error = error.response.data.log.error
          }

          if (error.response.status == 429) {
            // TODO review if this has to replace whole dict too...
            this.error.rate_limit = "Too many requests, please try again later."
          }
          if (error.response.status == 403) {

            // CAUTION must replace dict, if just do the key thing it doesn't seem to detect
            // change as expected.
            this.error = {'permission' : "Invalid permission."}
          }
        }

      });
    }
  }
}

) </script>
