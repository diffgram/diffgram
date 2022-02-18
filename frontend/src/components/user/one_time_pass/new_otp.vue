<template>
  <div v-cloak>
    <v-flex xs6 center>


      <v-container>

        <v-alert type="error" :value="has_error">
          {{error_list}}
        </v-alert>

        <div v-if="!$store.state.user.current.otp_enabled">
          <v-btn color="success"
                  :loading="loading"
                  @click="enable_otp"
                  :disabled="loading">
            Enable
          </v-btn>
        </div>

          <v-alert type="success" :value="backup_code_list">
            Enabled!

            Keep a copy of your backup access codes in a safe place:
            <ul>
              <li v-for="code in backup_code_list">
                {{code}}
              </li>
            </ul>
          </v-alert>

          <div v-if="otp">
            Scan with your Google Authenticator or other OTP app
            <qriously :value="qr_code_url" :size="200"></qriously>

            <v-alert type="warning" >
              These codes will not be visible again.
            </v-alert>
          </div>

      </v-container>


    </v-flex>
  </div>
</template>

<script lang="ts">

import axios from '../../../services/customAxiosInstance';

import Vue from "vue"; export default Vue.extend( {
  name: 'new_otp',
  data() {
    return {
      loading: false,

      has_error: false,
      error_list: [],
      otp: null,
      qr_code_url: "",
      backup_code_list: null,
    }
  },

  computed: {

  },

  created() {

  },

  destroyed() {
    this.qr_code_url = "",
    this.backup_code_list = null
  },

  methods: {
    enable_otp: function () {

      this.loading = true;

      axios.post('/api/user/otp/enable', {

      }).then(response => {

        if (response.data['success'] == true) {

          this.otp = response.data.otp
          this.qr_code_url = response.data.qr_code_url
          this.backup_code_list = response.data.backup_code_list

          this.$store.commit('set_current_user', response.data.user)

        } else {

          console.error(response)

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
