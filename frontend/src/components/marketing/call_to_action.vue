<template>
<div >

<div class="text-center">

  <!-- Hide on mobile because
    site is not designed to work for mobile
    -->

  <v-btn
      class="hidden-sm-and-down"
      color="primary"
      large
      rounded
      dark
      @click="$router.push('/user/new')">
  <v-icon left>mdi-flash-circle</v-icon>
  Try Now
  </v-btn>

  <v-btn
      v-if="show_learn_more == true"
      large
      rounded
      class="white--text"
      color="green"
      @click="$router.push('/demos')"
      >
  <v-icon left>mdi-video</v-icon>
  Learn More
  </v-btn>

  <v-btn
      large
      rounded
      class="white--text"
      color="amber darken-2"
      @click="$router.push('/enterprise/contact')"
      >
  <v-icon left>mdi-send</v-icon>
    Contact Sales
  </v-btn>

</div>

  <!--
<div class="text-center pt-2">
  <h4>
    Join over 2,000 people using Diffgram today!
  </h4>
</div>
    -->

</div>
</template>

<script lang="ts">

import Vue from "vue";

export default Vue.extend( {

  props: {
    'show_learn_more': {
      default: true,
      type: Boolean
    },
  },

  name: 'call_to_action',
  data () {
    return {

    }
  },

  methods: {

  }
}
) </script>

