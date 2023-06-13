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

        <standard_button
            v-if="enable_view_existing"
            tooltip_message="View Existing"
            @click="view_existing_open = true"
            icon="mdi-account-multiple"
            :icon_style="true"
            color="primary">
        </standard_button>

        <!-- All this button does is toggle the member_kind
            instead of user having to "know" to do it in select.
            -->
        <standard_button
          v-if="member_kind == 'User' && show_sdk_share"
          tooltip_message="Developer Authentication (API/SDK)"
          @click="member_kind = 'Developer Authentication (API/SDK)'"
          icon="mdi-key-plus"
          :icon_style="true"
          color="primary"
          :disabled="loading"
                        >
        </standard_button>

        <standard_button
          v-if="member_kind != 'User'"
          tooltip_message="Invite User"
          @click="member_kind = 'User'"
          icon="mdi-account"
          :icon_style="true"
          color="primary"
          :disabled="loading"
                        >
        </standard_button>

      </v-card-title>

      <v-container>

        <v-alert type="error" :value="errors">
          {{errors}}
        </v-alert>


        <v-select v-if="member_kind == 'Developer Authentication (API/SDK)'"
                  :items="member_kind_list"
                  v-model="member_kind"
                  label="Member type"
                  item-value="text"
                  :disabled="loading"
                  prepend-icon="mdi-security-account"></v-select>

        <v-dialog v-model="view_existing_open"
                  id="view_existing_members"
                  v-if="enable_view_existing"
                  width="800px">
          <v-card>
            <v-container>

              <v-card-title>
                Existing

                <v-spacer></v-spacer>
                <standard_button
                  tooltip_message="Close"
                  @click="view_existing_open = !view_existing_open"
                  icon="mdi-close"
                  :icon_style="true"
                  color="primary"
                  :bottom="true"
                  datacy="close-view_existing_open"
                  class="text-right"
                >
                </standard_button>
              </v-card-title>

              <v_collaborate_list_existing :project_string_id="project_string_id">
              </v_collaborate_list_existing>

              Invited users not shown.

            </v-container>
          </v-card>
        </v-dialog>

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

          <v-layout>
            <diffgram_select
                :item_list="permission_type_list"
                v-model="permission_type"
                label="Select Permission"
                :disabled="loading"
                prepend_icon="security"
                >
            </diffgram_select>

            <standard_button
                tooltip_message="Help"
                href="https://diffgram.readme.io/docs/project#project-roles"
                target="_blank"
                icon="help"
                :icon_style="true"
                color="primary">
            </standard_button>

          </v-layout>

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


    <free_tier_limit_dialog
      :message="message_free_tier_limit"
      :details="details_free_tier_limit"
      ref="free_tier_limit_dialog">

    </free_tier_limit_dialog>
  </div>
</template>

<script lang="ts">

import axios from '../../services/customInstance'
import auth_api_new from '../auth/api/auth_api_new'
import free_tier_limit_dialog from '../free_tier_limits/free_tier_limit_dialog'


import Vue from "vue"; export default Vue.extend( {
  name: 'share_new',
  components: {
    auth_api_new,
    free_tier_limit_dialog
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
    },
    'enable_view_existing':{
      default: true
    },
  },
  data() {
    return {

      loading: false,
      email: null,
      errors: null,
      note: null,
      result: null,

      view_existing_open: false,

      notify: true,

      error: {}, // new standard error
      message_free_tier_limit: '',
      details_free_tier_limit: '',
      // careful this is 'human' and 'api' on back end.
      member_kind_list: ['User', 'Developer Authentication (API/SDK)'],
      member_kind: 'User',

      permission_type_list: [
          { 'name': 'admin',
            'display_name': 'Admin - All functions in project.',
            'icon': 'mdi-shield-crown',
            'color': 'primary'
          },
          { 'name': 'Editor',
            'display_name': 'Editor - All except: add, remove, edit users.',
            'icon': 'mdi-account-edit',
            'color': 'primary'
          },
          { 'name': 'annotator',
            'display_name': 'Annotator - All task and annotation related functions.',
            'icon': 'mdi-account',
            'color': 'primary'
          },
          { 'name': 'Viewer',
            'display_name': 'Viewer - View only, no write access.',
            'icon': 'mdi-eye',
            'color': 'primary'
          }
      ],

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
          if(response['data']['errors']['free_tier_limit']){
            this.message_free_tier_limit = 'The invite failed because you reached a limit in the free tier of Diffgram.com hosted version. Upgrade or self-install.'
            this.details_free_tier_limit = response['data']['errors']['free_tier_limit']
            this.$refs.free_tier_limit_dialog.open();
          }
          else{
            this.errors = response.data['errors']
          }

          this.loading = false
        }
      })
      .catch(error => {
        this.loading = false

        // CAUTION these errors are for user only NOT auth API

         if (error.response) {
          if (error.response.status == 400) {
            if(error.response.data &&
              error.response.data.log &&
              error.response.data.log.error.free_tier_limit){
              this.message_free_tier_limit = 'The invite failed because you reached a limit in the free tier of Diffgram.com hosted version. Upgrade or self-install.'
              this.details_free_tier_limit = error.response.data.log.error.free_tier_limit;
              this.$refs.free_tier_limit_dialog.open();
            }
            else{
              this.error = error.response.data.log.error
            }

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
