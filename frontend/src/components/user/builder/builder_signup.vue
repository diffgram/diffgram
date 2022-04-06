<template>
  <div class="d-flex align-center justify-center screen-height" v-cloak>

    <v-col cols="9">

      <div class="pa-4">
        <v-card>

          <v-alert type="info"
                   v-if="error.general">
            {{error.general}}
          </v-alert>

          <div class="pt-4 ma-auto text-center" style="width: 100%">
            <img
              src="https://storage.googleapis.com/diffgram-002/public/logo/diffgram_logo_word_only.png"
              height="60px"
            />
          </div>

          <v-card-title>
            <h3 class="headline">A journey of a thousand miles continues with this step</h3>
          </v-card-title>

          <v-container>

            <v-layout>

              <v-flex xs12 sm6>
                <v-text-field
                  label="*First name"
                  data-cy="first_name"
                  v-model="first_name"
                  :disabled="loading"
                />
                <v-alert
                  type="info"
                  v-if="error.first_name"
                >
                  {{error.first_name}}
                </v-alert>
              </v-flex>

              <div style="width: 10px" />

              <v-flex xs12 sm6>
                <v-text-field
                  label="*Last name"
                  data-cy="last_name"
                  v-model="last_name"
                  :disabled="loading"
                />
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
                <v-text-field
                  label="*City"
                  data-cy="city"
                  v-model="city"
                  :disabled="loading"
                />
                <v-alert type="info"
                         v-if="error.city">
                  {{error.city}}
                </v-alert>
              </v-flex>

              <div style="width: 10px" />

              <v-flex>
                <v-text-field
                  label="*Company or Institution"
                  data-cy="company"
                  v-model="company"
                  :disabled="loading"
                />
                <v-alert type="info"
                         v-if="error.company">
                  {{error.company}}
                </v-alert>
              </v-flex>


              <div style="width: 10px" />

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
              <v-flex>
                <v-text-field label="How did you hear about us?"
                              data-cy="how_hear_about_us"
                              v-model="how_hear_about_us"
                              :disabled="loading"
                              >
                </v-text-field>
              </v-flex>


              <div style="width: 10px" />

              <diffgram_select
                  v-if="role != 'student'"
                  :item_list="demo_list"
                  v-model="demo"
                  data-cy="demo_select"
                  label="Are you interested in purchasing Enterprise?"
                  :disabled="loading"
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
                  v-model="how_many_data_labelers"
                  :disabled="loading"
                        >
              </v-slider>
            </v-layout>

            <v-card-actions class="pt-2">
              <v-btn  color="primary"
                      block
                      @click="builder_enable_api"
                      data-cy="finish_singup_button"
                      :disabled="loading"
                >
               <v-icon left> mdi-flag-checkered </v-icon>
                  Finish
              </v-btn>
            </v-card-actions>

          </v-container>

          <v-progress-linear
            v-if="loading"
            attach
            indeterminate
            height="20">

          </v-progress-linear>

        </v-card>

      </div>


    </v-col>



  </div>
</template>

<script lang="ts">

  import axios from '../../../services/customInstance';
  import {getProject} from '../../../services/projectServices'
  import Vue from "vue"; export default Vue.extend( {
    name: 'builder_signup',
    data() {
      return {
        loading: false,

        how_many_data_labelers: 0,
        how_many_data_labelers_tick_labels: [
          "None yet",
          "5 or less",
          "25 or less",
          "100+"
        ],

        first_name: String,
        last_name: String,
        phone_number: null,
        city: null,
        company: null,
        project_string_id_param: null,
        user_role: null,
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
            { 'name': 'sales',
              'display_name': 'Yes. (Sales will contact you)',
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
      this.project_string_id_param = this.$route.query["project_string_id"]
      this.user_role = this.$route.query["role"]

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
            this.loading = false
          }


        })
          .catch(error => {
            console.error(error);
            this.loading = false
          });
      },

      route_new_project: async function () {
        if(this.project_string_id_param){
          let [project_data, error] = await getProject(this.project_string_id_param)

          this.$store.commit('set_project', project_data.project)
          if(error){
            this.error = this.$route_api_errors(error)
            this.loading = false
          }
        }
        if(this.user_role === 'Editor'){
          this.$router.push('/welcome')
        }
        else{
          this.$router.push('/welcome')
        }
      },

    }
  }

) </script>
