<template>
<div id="pricing">

  <v-layout justify-space-around>
    <v-flex md9 lg8>

    <v-container>
      <v-card>

      <v-card elevation-1 color="primary">
        <h1 class="white--text text-center pt-4">
          Confirm {{ name }} Order
        </h1>
        <h2 class="grey--text text--lighten-4 text-center pa-4">

        </h2>
      </v-card>


        <!-- CREDIT CARD -->

        <credit_card show_account_info=false>
        </credit_card>


        <v-card>

          <!-- TODO insert plan info -->

          <v-flex class="pa-4">

            <v-btn color="primary"
                   :disabled="loading"
                   @click="order()"
                   >
              Confirm {{name}}
            </v-btn>

              <v-alert type="success"
                       :value="success">

                Welcome! You are on now the {{ name }} plan!

              </v-alert>

              <v_error_multiple :error="error">
              </v_error_multiple>

          </v-flex>
        </v-card>
        

        <sub class="pa-4"> Terms and conditions apply.
    See <a @click="$router.push('/policies')"> policies </a>
    for more info. </sub>

        </v-card>
      </v-container>
    </v-flex>
  </v-layout>

</div>
</template>

<script lang="ts">

import axios from 'axios';
import credit_card from './credit_card'

import Vue from "vue"; export default Vue.extend( {
  name: 'order',
  components: { credit_card },
  data () {
    return {

      name: null,
      error: {},
      success: false,
      loading: false
      
    }
  },
  created() {

    this.name = this.$route.query["name"]

  },
  methods: {
    
    order: function() {

      this.loading = true
      this.error = { }

      axios.post('/api/v1/project/'
        + this.$store.state.project.current.project_string_id
        + '/account/plan/new', {

          'plan_template_public_name': this.name

      })
      .then(response => {

        this.success = true
        this.loading = false

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
        }
      });

    }
  }
}
) </script>

