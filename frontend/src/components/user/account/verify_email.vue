<template>
  <div>
    <v-container>
      <br />
      <v-card>

        <v-card-title>
          <h3 class="headline">Email verification</h3>
        </v-card-title>

        <v-card-text>

          <v-alert type="success" :value="verify_success">
            Thank you for verifying your email!
          </v-alert>

          <v-alert type="info" :value="verify_error">
            {{verify_error}}
          </v-alert>

        </v-card-text>

        <v-card-actions>
          <v_resend_verify_email v-if="!auth_code" />
        </v-card-actions>

      </v-card>
    </v-container>
  </div>
</template>

<script lang="ts">

import axios from '../../../services/customInstance';

import Vue from "vue"; export default Vue.extend( {
  name: 'user_account_verify_email',
  props: {
    'auth_code': {
      default: null
    },
    'email': {
      default: null
    }
  },
  data() {
    return {

      loading: false,

      verify_success: false,
      verify_error: false

    }
  },

  computed: {

  },

  created() {

    this.redeem_verify_via_email_api()

  },

  methods: {

    redeem_verify_via_email_api: function () {

      if (this.auth_code == undefined) {
        return
      }

      this.loading = true;

      axios.post('/api/v1/user/verify', {

        auth_code: this.auth_code,
        email: this.email

      }).then(response => {

        if (response.data.log.success == true) {

          this.verify_success = true
          this.$store.commit('patch_current_user', ['security_email_verified', true])

        } else {

          this.verify_error = response.data.log.error.auth_code

        }
        this.loading = false

      })
        .catch(error => {
          console.error(error);
          this.loading = false
        });
    }
  }
}

) </script>
