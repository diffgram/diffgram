<template>
  <div v-cloak>

    <v-col cols="9">

      <div class="pa-4">
        <v-card>

          <v-alert type="info"
                   v-if="error.general">
            {{error.general}}
          </v-alert>

          <v-container>

            <v-card-title>
              <h3 class="headline">Almost there!</h3>
            </v-card-title>

            <v-layout >

              <v-flex xs12 sm6>
                <v-text-field label="First name"
                              data-cy="first_name"
                              v-model="first_name">
                </v-text-field>
                <v-alert type="info"
                         v-if="error.first_name">
                  {{error.first_name}}
                </v-alert>
              </v-flex>
              <v-flex xs12 sm6>
                <v-text-field label="Last name"
                              data-cy="last_name"
                              v-model="last_name">
                </v-text-field>
                <v-alert type="info"
                         v-if="error.last_name">
                  {{error.last_name}}
                </v-alert>
              </v-flex>

            </v-layout>

            <v-layout >

              <!--
              <v-flex>
                <v-text-field label="Phone"
                              v-model="phone_number">
                </v-text-field>
                <v-alert type="info"
                         v-if="error.phone_number">
                  {{error.phone_number}}
                </v-alert>
              </v-flex>
                -->

              <v-flex>
                <v-text-field label="How did you hear about us?"
                              data-cy="how_hear_about_us"
                              v-model="how_hear_about_us">
                </v-text-field>
              </v-flex>

              <v-flex>
                <v-text-field label="City"
                              data-cy="city"
                              v-model="city">
                </v-text-field>
                <v-alert type="info"
                         v-if="error.city">
                  {{error.city}}
                </v-alert>
              </v-flex>

              <diffgram_select
                  data-cy="role"
                  :item_list="role_list"
                  v-model="role"
                  label="Role"
                  :disabled="loading"
                  >
              </diffgram_select>

            </v-layout>

            <v-layout >

              <v-flex md6>
                <v-text-field label="Company or Institution"
                              data-cy="company"
                          v-model="company">
                </v-text-field>
                <v-alert type="info"
                         v-if="error.company">
                  {{error.company}}
                </v-alert>
              </v-flex>

              <diffgram_select
                  v-if="role != 'student'"
                  :item_list="demo_list"
                  v-model="demo"
                  data-cy="demo_select"
                  label="Are you interested in an Enterprise Demo?"
                  >
              </diffgram_select>

            </v-layout>


            <v-layout>
              <v-slider
                  v-if="role != 'student'"
                  label="About how many Data Labelers?"
                  min=0
                  max=3
                  hint="On current team including outsourcing."
                  prepend-icon="mdi-account-group"
                  :tick-labels="how_many_data_labelers_tick_labels"
                  dense
                  ticks="always"
                  tick-size="4"
                  step=1
                  data-cy="how_many_data_labelers"
                  v-model="how_many_data_labelers">
              </v-slider>
            </v-layout>

            <v-card-actions>
              <v-btn  color="primary"
                      :loading="loading"
                      large
                      @click.native="loader = 'loading'"
                      @click="builder_enable_api"
                      data-cy="finish_singup_button"
                      :disabled="loading">
                Finish Signup
                <v-icon right> mdi-flag-checkered </v-icon>
              </v-btn>
            </v-card-actions>

          </v-container>
        </v-card>

      </div>



      <div class="pl-4 pr-4">
        <v-card>

          <v-alert  type="info"
                    color="grey"
                    >
            We protect information.

              <v-btn color="white"
                  outlined
                  href="/policies"
                  target="_blank">
            Data Policies
            <v-icon right>mdi-open-in-new</v-icon>
              </v-btn>

          </v-alert>

        </v-card>
      </div>
    </v-col>



  </div>
</template>

<script lang="ts">

  import axios from 'axios';

  import Vue from "vue"; export default Vue.extend( {
    name: 'builder_signup',
    data() {
      return {
        loading: false,

        how_many_data_labelers: 0,
        how_many_data_labelers_tick_labels: [
          "None yet",
          "5",
          "25",
          "250+"
        ],

        first_name: String,
        last_name: String,
        phone_number: null,
        city: null,
        company: null,
        how_hear_about_us: null,
        demo: null,

        error: {
          general: null,
          first_name: null,
          last_name: null,
          phone_number: null,
          city: null,
          company: null
        },

        role: null,

        role_list: [
          { 'name': 'leadership',
            'display_name': 'Leadership',
            'icon': 'mdi-account-supervisor',
            'color': 'primary'
          },
          { 'name': 'product',
            'display_name': 'Product',
            'icon': 'mdi-codepen',
            'color': 'primary'
          },
          { 'name': 'engineering',
            'display_name': 'Engineering, Technical',
            'icon': 'mdi-code-braces',
            'color': 'primary'
          },
          { 'name': 'student',
            'display_name': 'Student, Student Researcher',
            'icon': 'mdi-book-open-variant',
            'color': 'primary'
          },
          { 'name': 'other',
            'display_name': 'Other',
            'icon': 'check',
            'color': 'primary'
          }
        ],

        demo_list: [
            { 'name': 'demo',
              'display_name': 'Yes, a Technical Demo.',
              'icon': 'mdi-monitor-screenshot',
              'color': 'primary'
            },
            { 'name': 'sales',
              'display_name': 'Please have Sales email me.',
              'icon': 'mdi-currency-usd',
              'color': 'primary'
            },
            { 'name': 'not_yet',
              'display_name': 'Not yet.',
              'icon': 'mdi-timer',
              'color': 'primary'
            }
        ],


        signup_code: null,
        error_signup_code: null  // Optional


      }
    },

    computed: {

    },

    created() {

      this.first_name = this.$store.state.user.current.first_name
      this.last_name = this.$store.state.user.current.last_name
      this.signup_code = this.$route.query["code"]

    },

    methods: {
      builder_enable_api: function () {

        this.loading = true;

        // reset error
        this.error = {
          general: null,
          first_name: null,
          last_name: null,
          phone_number: null,
          city: null,
          company: null
        }

        axios.post('/api/v1/user/builder/enable', {

            'first_name': this.first_name,
            'last_name': this.last_name,
            //'phone_number': this.phone_number,
            'how_hear_about_us': this.how_hear_about_us,
            'city': this.city,
            'company': this.company,
            'role': this.role,
            'demo': this.demo,
            'how_many_data_labelers': this.how_many_data_labelers_tick_labels[this.how_many_data_labelers]

        }).then(response => {


          if (response.data.log.success == true) {

            this.$store.commit('set_mode_builder')

            // especially relevant in context of new user
            // since they have just provided new info, but not
            // done any other actions to refresh user information
            this.$store.commit('set_current_user', response.data.user)

            this.route_new_project()

          } else {
            this.error = response.data.log.error
          }

          this.loading = false


        })
          .catch(error => {
            console.log(error);
            this.loading = false
          });
      },

      route_new_project: function () {
        this.$router.push('/a/project/new?builder_api_enabled_success=true')
      }

    }
  }

) </script>
