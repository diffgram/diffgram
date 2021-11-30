<template>
  <div>

    <v-container>

      <h1 class="pa-4">Markets</h1>

      <v-card>

        <img src="">

        <!-- Retail / Cashiers -->
        <img src="https://storage.googleapis.com/diffgram_public/marketing/markets/Market%20-%20Retail%20cashiers.svg">

        <!-- Food prep-->
        <img src="https://storage.googleapis.com/diffgram_public/marketing/markets/Market%20-%20food%20prep%20part%201.svg">

        <!-- Office / knowledge work-->
        <img src="https://storage.googleapis.com/diffgram_public/marketing/markets/Market%2C%20office%20part%201.svg">


        <div class="text-center pb-4">
          <v-btn color="primary"
                 large
                 @click="$router.push('/enterprise/contact')">
            Connect with us
            <v-icon right>mdi-flash-circle</v-icon>
          </v-btn>
        </div>


      </v-card>
    </v-container>

  </div>
</template>

<script lang="ts">


import Vue from "vue"; export default Vue.extend( {
  name: 'markets',
  data () {
    return {

    }
  },
  created() {

  },
    mounted() {

  },

  methods: {

  }
}
) </script>

