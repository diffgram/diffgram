<template>
  <div id="request_updates">

    <v_request_updates :request_name = "request_name">
    </v_request_updates>

  </div>
</template>

<script lang="ts">

  import Vue from "vue"; export default Vue.extend( {
    name: 'request_updates_generic',

    data() {
      return {
        request_name: "updates"
      }
    },
    created() {
    },
    methods: {
    }
  }
) </script>

