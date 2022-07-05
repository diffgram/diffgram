
<template>
  <div class="d-flex align-center justify-center screen-height flex-column" v-cloak v-if="!logout_loading">
    <v_error_multiple :error="error_logout"></v_error_multiple>
    <div>

      <v-alert type="info"><h3> You Are Now Logged Out</h3> </v-alert>

      <v-btn x-large @click="go_to_login">Log In Again</v-btn>
    </div>
  </div>
  <div v-else class="d-flex justify-center flex-column align-center">
      <div class="ma-auto mt-12" style="border: 1px solid #e0e0e0; width: 650px; height: 150px">
        <h1 class="text-center mt-6"> Logging out...</h1>
        <v-progress-linear indeterminate></v-progress-linear>
      </div>
  </div>
</template>

<script lang="ts">
import { logout } from "../../services/userServices"
import Vue from "vue";
export default Vue.extend({
  name: "logout",
  props: {
    magic_auth: {
      default: null,
    },
    no_redirect: {
      default: null,
    },
  },
  data() {
    return {
      e1: true,
      email: null,
      mode: "loading",
      show_logging_in_messsage: false,
      error_logout: null,
      logout_loading: true,
      password: null,
    };
  },
  async mounted() {


    await this.do_logout()

  },
  destroyed() {

  },
  methods: {
    go_to_login: function(){
      this.$router.push("/user/login");
    },
    do_logout: async function(){
      this.error_logout = null
      let [result, err] = await logout()
      if(err){
        this.error_logout = this.$route_api_errors(err)
      }
      this.logout_loading = false

    }


  },
});
</script>
