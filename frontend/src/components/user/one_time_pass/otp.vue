<template>
  <div>

    <v-card>

      <v-card-title>
        <h3 class="headline">2 Factor Authentication</h3>
      </v-card-title>

      <div v-if="$store.state.user.current.otp_enabled">
        <v-alert type="success" >
          On
        </v-alert>

        <v-btn color="error"
               :loading="loading"
               @click="disable_otp"
               :disabled="loading">
          Disable
        </v-btn>

      </div>

      <div v-else>
        <v-alert type="error" >
          Off
        </v-alert>
      </div>

      <v_user_new_otp>
      </v_user_new_otp>

    </v-card>

  </div>
</template>

<script lang="ts">

import axios from 'axios';

import Vue from "vue"; export default Vue.extend( {
  name: 'otp',
  data() {
    return {

      loading: false

    }
  },

  computed: {

  },

  created() {

  },

  methods: {

    disable_otp: function () {

      this.loading = true;

      axios.post('/api/user/otp/disable', {

      }).then(response => {

        if (response.data['success'] == true) {

          this.$store.commit('set_current_user', response.data.user)

        } else {


        }
        this.loading = false

      })
        .catch(error => {
          console.log(error);
          this.loading = false
        });
    }
  }
}

) </script>
