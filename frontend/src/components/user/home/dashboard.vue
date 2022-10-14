<template>
  <div id="home" class="home-container">

    <div v-if="$store.state.user.logged_in == true">
      <div v-if="!$store.state.builder_or_trainer.mode">
        <v-card>

          <v-alert type="success"

          >
            Account created! Now enable the builder API
          </v-alert>

          <v-container>

            <v-layout>
              <v-flex xs12>

                <v-card>

                  <div class="text-center pa-4">
                    <v-btn large
                           outlined
                           color="primary"
                           @click="route_builder_signup()">
                      Resume Onboarding
                    </v-btn>
                  </div>

                </v-card>

              </v-flex>

            </v-layout>
          </v-container>


        </v-card>
      </div>

      <br />

      <v-card
        v-if="$store.state.user.current.security_email_verified != true">
        <v-card-title>
          <h3 class="font-weight-light ml-4">
              Please verify your email: {{$store.state.user.current.email}}</h3>
        </v-card-title>

        <p>Actions are restricted until verification.</p>

        <v-card-actions>
          <v_resend_verify_email />
        </v-card-actions>

      </v-card>

      <br />


      <v-card v-if="$store.state.builder_or_trainer.mode == 'builder'
            && !$store.state.project.current.project_string_id">
        <v-card-title>Actions</v-card-title>

        <v-card-text>
          <p>Diffgram quick start:</p>
          <ul>
            <li>
              <a target= "_blank" href="https://diffgram.readme.io/docs/diffgram-101-key-concepts#project">Diffgram 101 - Key Concepts</a>
            </li>
            <li>
              <a target= "_blank" href="https://diffgram.readme.io/docs/data-scope-introduction">Datasets</a>
            </li>
            <li>
              <a target= "_blank" href="https://diffgram.readme.io/docs/tasks">Tasks</a>
            </li>
            <li>
              <a target= "_blank" href="https://diffgram.readme.io/docs/project">Share a project</a>
            </li>
            <li>
              <a target= "_blank" href="https://diffgram.readme.io/docs/the-diffgram-python-sdk">Python SDK</a>
            </li>
          </ul>
          <br />
          <p>More doc you can find <a target= "_blank" href="https://diffgram.readme.io">here</a></p>
        </v-card-text>

        <v-card-actions>
          <v-btn large
                color="primary"
                @click="$router.push('/welcome')">
            Resume Onboarding
          </v-btn>

          <v-btn large
                color="primary"
                @click="$router.push('/a/project/new')">
            New Project
          </v-btn>

          <v-btn large
                 color="primary"
                 @click="$router.push('/projects')">
            Change Project
          </v-btn>

        </v-card-actions>
      </v-card>

      <div v-if="$store.state.builder_or_trainer.mode == 'builder' &&
               $store.state.project.current.project_string_id">

        <h1 class="black--text text--lighten-2 text-center pa-4">
          {{$store.state.user.current.first_name}}, welcome back!
        </h1>

        <v-layout>
          <v-row>
<!--            <v-col cols="3">-->
<!--              <v-card>-->
<!--                <v-card-title>Visit History:</v-card-title>-->
<!--                <v-card-text>-->
<!--                  <user_visit_history_list :project_string_id="project_string_id"></user_visit_history_list>-->
<!--                </v-card-text>-->
<!--              </v-card>-->
<!--            </v-col>-->
            <v-col cols="12">

              <v-card >
                <v-card-title>Reports: </v-card-title>
                <!-- Note we assume default dashboard is ok here -->
                <report_dashboard
                  v-if="$store.state.builder_or_trainer.mode == 'builder'"
                  :report_dashboard_id="$store.state.project.current.default_report_dashboard_id"
                >
                </report_dashboard>

              </v-card>
            </v-col>

          </v-row>
        </v-layout>
        <div v-if="$store.state.builder_or_trainer.mode == 'builder'"
             class="text-center"
        >


        </div>
      </div>

      <div v-if="$store.state.user.settings.show_ids == true">
        Project ID {{$store.state.project.current.id}}
      </div>
    </div>

    <div v-if="$store.state.user.logged_in != true">
      <v-container>

        <v-layout>
          <v-flex xs12>

            <v-card>

              <!-- TODO include more context, ie the project invited to etc. etc -->

              <h1 class="black--text text--lighten-2 text-center pt-4">
                Welcome to Diffgram!
              </h1>

              <h2 class="blue--text text--lighten-1 text-center pa-2">
                Please login to start:
              </h2>

              <div class="text-center pa-4">
                <v-btn large
                       outlined
                       color="primary"
                       @click="route_login">
                  Login
                </v-btn>
              </div>

            </v-card>

          </v-flex>

        </v-layout>
      </v-container>
    </div>
  </div>
</template>

<script lang="ts">

import Vue from "vue";
import report_dashboard from '../../report/report_dashboard.vue'
import user_visit_history_list from '../../event/user_visit_history_list.vue'
import project_pipeline from '../../project/project_pipeline.vue'

export default Vue.extend( {
  name: 'user_dashboard',
  components: {
    report_dashboard,
    user_visit_history_list,
    project_pipeline,

  },
  data () {
    return {


    }
  },
  created() {

  },
  mounted() {

  },
  computed: {
    project_string_id: function(){
      return this.$store.state.project.current.project_string_id;
    }
  },
  methods: {
    route_trainer_signup: function () {
      this.$router.push('/user/trainer/signup')
    },
    route_login: function () {
      this.$router.push('/user/login')
    },
    route_builder_signup: function () {
      this.$router.push('/user/builder/signup')
    }
  }
}
) </script>
<style scoped>
  .home-container{
    padding: 0 10rem;
  }
</style>

