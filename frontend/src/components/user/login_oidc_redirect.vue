
<template>
  <div class="d-flex align-center justify-center screen-height" v-cloak>
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

  },
  destroyed() {

  },
  methods: {
    route_account_new: function () {
      this.$router.push("/user/new");
    },
    login: async function (code) {
      this.loading = true;
      try{
        const response = await axios.post(`/api/v1/auth/oidc-login`, {
          code: code
        })
        this.loading = false;

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
