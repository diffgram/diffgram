<template>
  <div>

    <v-sheet fluid>

      <div class="d-flex align-center justify-center screen-height"
           style="max-height: 600px">
        <div>
          <div class="text-center">
              <v-icon size="200">mdi-email</v-icon>
          </div>
          <h1 ><span class="hero">Verify your email</span></h1>

          <div class="text-center pa-4">
              <h2 class="font-weight-light"> {{$store.state.user.current.email}} </h2>

              <div v-if="success_state == false">
                <div class="pa-4">
                  <p v-if="is_automatically_checking == true">
                  This page will automatically reload
                  </p>
                </div>

                <tooltip_button
                  v-if="is_automatically_checking == false"
                  tooltip_message="Refresh"
                  @click="attempts = 0, is_user_verified_interval()"
                  :disabled="loading"
                  color="primary"
                  icon="mdi-refresh"
                  :icon_style="true"
                  :bottom="true"
                >
                </tooltip_button>

                <div style="min-height: 30px"> </div>

                <v_resend_verify_email v-if="is_automatically_checking == false"
                                       @security_email_verified="declare_success()"/>
              </div>

          </div>

        <v_error_multiple :error="error">
        </v_error_multiple>
        </div>
      </div>

    </v-sheet>

  </div>
</template>


<script lang="ts">
import Vue from 'vue'

import { is_user_verified } from "../services/userServices";
import { is_mailgun_set } from "../services/configService";

export default Vue.extend( {
  name: 'welcome_verify',
  props: {

  },

  data () {
    return {
       error: {},
       loading : false,
       security_email_verified: false,
       is_automatically_checking: true,
       intervel: undefined,
       attempts: 0,
       max_attempts: 300,
       check_intervel: 2000,
       mailgun: undefined,
       success_state: false
    }
  },
  watch: {

  },
  async created() {
    const { mailgun } = await is_mailgun_set()
    this.mailgun = mailgun
    if (this.mailgun == true) {
      this.is_user_verified_interval()
    } else {
      this.declare_success()
    }

  },
  computed: {

  },
  methods: {

    async is_user_verified_interval() {
      this.is_automatically_checking = true
      this.is_user_verified_api()
      this.intervel = setInterval(this.is_user_verified_api, this.check_intervel)
    },

    declare_success() {
      this.success_state = true
      clearInterval(this.intervel)
      this.is_automatically_checking = false
      this.$store.commit('patch_current_user', ['security_email_verified', true])
      this.$router.push('/welcome/adventure')
    },

    async is_user_verified_api() {
      this.attempts += 1
      if (this.attempts > this.max_attempts){
        clearInterval(this.intervel)
        this.is_automatically_checking = false
        return
      }
      this.loading = true
      this.error = undefined
      let result = await this.is_user_verified_generic(is_user_verified)
      this.error =  result[1]
      if (result[0].data) {
        let data = result[0].data
        if (data && data.security_email_verified) {
          this.security_email_verified = data.security_email_verified
          if (this.security_email_verified == true ) {
            this.declare_success()
          }
        }
      }
      this.loading = false
    },

    async is_user_verified_generic(api) {

      let result = await api()
      let error = this.$route_api_errors(result)
      return [result, error]
    },
    
  }
}
) </script>

<style>
  .hero {
    font-size: 2em;
  }
</style>
