<template>
  <div id="signup_beta">

    <v_request_updates :request_name="request_name">
    </v_request_updates>

  </div>
</template>

<script lang="ts">

  import Vue from "vue"; export default Vue.extend( {
    name: 'signup_beta',

    data() {
      return {
        request_name: "signup for beta"
      }
    },
    created() {
    },
    methods: {
    }
  }
) </script>

