
<template>
  <div class="d-flex align-center justify-center screen-height flex-column" v-cloak>
    <v_error_multiple :error="error_login"></v_error_multiple>
    <div>
      <v-progress-linear
        height="10"
        indeterminate
        absolute
        top
        color="secondary accent-4"
      >
      </v-progress-linear>

      <v-alert type="info"> Logging in... </v-alert>
    </div>
  </div>
</template>

<script lang="ts">
import axios from "../../services/customInstance";
import { is_mailgun_set } from "../../services/configService";

import Vue from "vue";
import {auth_redirect} from "./account/auth_redirect";
export default Vue.extend({
  name: "user_login",
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
      error_login: null,
      password: null,
    };
  },
  async created() {
    if (this.$store.state.user.logged_in == true){
      if ("redirect" in this.$route.query) {
        this.$router.push(this.$route.query["redirect"]);
      }
      else{
        this.$router.push('/home/dashboard');
      }
    }

    await this.oidc_login(this.$route.query.code)

  },
  destroyed() {

  },
  methods: {
    route_account_new: function () {
      this.$router.push("/user/new");
    },
    oidc_login: async function (code) {
      this.loading = true;
      try{
        const response = await axios.post(`/api/v1/auth/oidc-login`, {
          code: code
        })
        this.loading = false;
        if(response.data.new_user_created){
          if (response.data.user) {
            this.$store.commit('set_current_user', response.data.user)
          }

          // careful must return after matching
          // routing condition otherwise goes to next value one...

          if (this.user_kind == "annotator_signup") {
            this.$router.push('/user/trainer/signup')
            return
          }

          let auth = response.data.log.auth

          auth_redirect(auth, response.data.project_string_id, this.$router, this.$store)
        }
        this.do_login(response);

      }
      catch (error){
        console.error(error)
        this.loading = false;
        this.error_login = this.$route_api_errors(error)
        if (error.response) {
          if (error.response.status == 400) {
            this.error = error.response.data.log.error;
          }

          if (error.response.status == 429) {
            this.error.rate_limit =
              "Rate Limited. Too many requests, please try again later.";
          }
        }
      }

    },
    do_login: function (response) {
      this.show_logging_in_messsage = true;

      this.$store.commit("log_in");

      if (response.data.user.last_builder_or_trainer_mode == "trainer") {
        this.$store.commit("set_mode_trainer");
      }
      if (response.data.user.last_builder_or_trainer_mode == "builder") {
        this.$store.commit("set_mode_builder");
      }
      let user = {
        ...response.data.user,
        install_fingerprint: response.data.install_fingerprint
      }
      this.$store.commit("set_current_user", user);

      if (response.data.user.org_default) {
        // TODO not clear if null check is needed here
        if (response.data.user.org_default != null) {
          this.$store.commit("set_org", response.data.user.org_default);
        }
      }

      if (this.no_redirect == true) {
      } else {
        if ("redirect" in this.$route.query) {
          this.$router.push(this.$route.query["redirect"]);
        } else {

          let project_current = response.data.user.project_current;
          if (project_current) {
            this.$store.commit(
              "set_project_string_id",
              project_current.project_string_id
            );
            this.$store.commit("set_project_name", project_current.name);
            this.$store.commit("set_project", project_current);
          }

          this.$router.push("/home/dashboard");

        }
      }
    },
  },
});
</script>
