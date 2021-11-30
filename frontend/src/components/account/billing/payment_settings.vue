<template>
  <div>

    <h1 class="black--text text--lighten-2 text-center pt-4">
      Payment settings
    </h1>

    <credit_card></credit_card>

  </div>
</template>

<script lang="ts">


import axios from 'axios';
import credit_card from './credit_card'

import Vue from "vue"; export default Vue.extend( {
  name: 'payment_settings',
  components: { credit_card },
  props: [''],
  data() {
    return {

      account: {
        id: null
      },

      loading: false,
      errors: null,

    }
  },
  mounted() {


  },
  methods: {

  }
}

) </script>
