<template>

  <div id="">



      <!-- TODO proper check if already verified-->

      <v-btn @click="start_verify_via_email_api"
             color="primary"
             :loading="loading"
             v-if="!start_verify">
        Resend verify email
      </v-btn>

      <v-alert type="success"
               v-if="start_verify">
        Check your email. :)
      </v-alert>

      <v-alert type="info"
               v-if="error">
        {{error}}
      </v-alert>

  </div>

</template>

<script lang="ts">

import axios from '../../../services/customInstance';


import Vue from "vue"; export default Vue.extend( {
  name: 'resend_verify_email',
  props: [],

  data () {
    return {
      start_verify: false,
      loading: false,
      error: false
    }
  },
  created() {
  },
  computed: {
  },
  methods: {

    start_verify_via_email_api: function () {

      this.loading = true;
      this.error = false

      axios.get(
        '/api/v1/user/verify/start'
      ).then(response => {

        this.loading = false
        this.start_verify = true

      })
      .catch(error => {

        this.error = error.response.data.log.error.verify_error

        if (this.error == "Already verified.") {
          this.$store.commit('patch_current_user', ['security_email_verified', true])
        }

        console.error(error);
        this.loading = false
      });
    }
  }
}
) </script>
