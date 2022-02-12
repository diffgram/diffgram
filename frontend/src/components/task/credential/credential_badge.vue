<template>

  <v-card fluid class="ma-2" style="max-width: 150px">
    <img width="150" height="150" v-if="credential.image && credential.image.url_signed_thumb" :src="credential.image.url_signed_thumb" alt="">
    <v-icon v-else size="150" color="warning">mdi-shield-star</v-icon>
    <div class="d-flex justify-center">
      <p class="secondary--text font-weight-bold ma-auto text-center">{{credential.name}}</p>
    </div>

  </v-card>

</template>

<script lang="ts">

import Vue from "vue";

export default Vue.extend({
    name: 'credential_badge',
    props: {
      'credential': {
        default: null
      }
    },
    data() {
      return {

        loading: false,


      }
    },
    created() {

    },
    computed: {},

    methods: {}
  }
) </script>
