<template>
  <div v-cloak>

    <v-card elevation="0">
      <v-container>

        <v-card-title>
          <tooltip_icon
              color="primary"
              icon="mdi-database"
              tooltip_message="Data Platform"
              tooltip_direction="bottom"
              >
          </tooltip_icon>
          <h3 class="headline pl-2">Create your free Data Platform account now</h3>
        </v-card-title>

        <v_error_multiple :error="error"
                          data-cy="error-email">
        </v_error_multiple>

        <v-text-field label="Email"
                      v-model="email"
                      data-cy="email-input"
                      validate-on-blur
                      :rules="[rules.email]">
        </v-text-field>

        <v-btn color="primary"
               data-cy="create-user-button"
                :loading="loading"
                @click="new_user"
                :disabled="loading">
          Create
        </v-btn>


      <v-row>

        <v-col cols="3">

          <v-card elevation="0">

            <v-card-title>You're in great company</v-card-title>

            <v-card-text>
              Join over 6,000 users who have created over 3,000 projects
              and 50 million annotations with Diffgram.
            </v-card-text>

          </v-card>


        </v-col>


        <v-col cols="7">

          <div class="pa-4">
            <v-img
              class="pa-4"
              src="https://storage.googleapis.com/diffgram_public/marketing/Join_users_from_new.svg"
              contain
                    >
            </v-img>
          </div>

        </v-col>

        </v-row>

    </v-container>
  </v-card>

  </div>
</template>

<script lang="ts">

  import axios from 'axios';

  import Vue from "vue";

  export default Vue.extend( {
    name: 'user_data_platform_new',
    data() {
      return {
        loading: false,

        email: "",
        error: {},

        user_kind: null,

        signup_code: null, // Optional
        error_signup_code: null,

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

    },

    created() {

      this.$store.commit('set_mode_builder')

      this.user_kind = this.$route.query["user_kind"]

      this.email = this.$route.query["email"]
      this.signup_code = this.$route.query["code"]

      // log out by default (if logged in) since we will be putting a new cookie here
      // and edge case but would be strange if made new account and then didn't change
      // account stuff properly
      if (this.$store.state.user.logged_in == true) {
        this.logout()
      }
    },

    methods: {
      logout: function () {
        axios.get('/user/logout')
          .then(response => {
            this.$store.dispatch('log_out')
          })
          .catch(error => {
            console.error(error);
          });
      },
      new_user: function () {

        this.error = {}

        // Local test to avoid API call (spam). Note super happy with this here.
        if (this.email == undefined) {
          this.error['email'] = "Please enter an email"
          return
        }

        this.loading = true;

        axios.post('/api/v1/user/new', {
         'email': this.email,
         'signup_code': this.signup_code
        }).then(response => {



          this.$store.commit('log_in');
          this.$store.commit('set_user_name', this.email)
          if (response.data.user) {
            this.$store.commit('set_current_user', response.data.user)
          }

          // careful must return after matching
          // routing condition otherwise goes to next value one...

          if (this.user_kind == "annotator_signup") {
            this.$router.push('/user/trainer/signup')
            return
          }

          let auth = response.data.log.auth

          // TODO review more general use for this, as may be builder or trainer...
          if (auth) {
            if (auth.type == "invite_to_org") {

                if(["Admin"].includes(auth.user_permission_level)) {

                      this.$router.push('/user/builder/signup');
                  }

                if(auth.user_permission_level == "Annotator") {

                    this.$router.push('/user/trainer/signup');
                  }
            }
            if (auth.type == "add_to_project") {
              //this.$router.push('/studio/annotate/' + response.data.project_string_id);
              this.$router.push('/home/dashboard');
            }

            return
          }

          if (response.data.project_string_id == null) {
            this.$router.push('/user/builder/signup');
          } else {
            this.$router.push('/project/' + response.data.project_string_id);
            this.$store.commit('set_project_string_id', response.data.user.project_string_id)
          }


        })
          .catch(error => {
            this.error = this.$route_api_errors(error)
            this.loading = false
          });
      }
    }
  }

) </script>
