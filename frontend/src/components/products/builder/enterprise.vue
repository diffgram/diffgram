<template>
<div >
   
  <v-container>

    <h1 class="pa-4">Enterprise Deep Learning</h1>

    <v-card>

      <img src="">

      <!-- Technical Support -->
      <img src="https://storage.googleapis.com/diffgram_public/marketing/enterprise/Enterprise%20-%20support.svg">

      <div class="text-center pb-4">
        <v-btn color="primary"
               large
               @click="$router.push('/enterprise/contact')">
          Connect with us
          <v-icon right>mdi-flash-circle</v-icon>
        </v-btn>
      </div>

      <!-- Security and controls -->
      <img src="https://storage.googleapis.com/diffgram_public/marketing/enterprise/Enterprise%20-%20Controls%20_%20security.svg">

      <!-- Available -->
      <img src="https://storage.googleapis.com/diffgram_public/marketing/enterprise/Enterprise%20-%20available%20_%20reliable.svg">

      <div class="text-center pb-4">
        <v-btn color="primary"
               large
               @click="$router.push('/enterprise/contact')">
          Connect with us
          <v-icon right>mdi-flash-circle</v-icon>
        </v-btn>
      </div>

      <!-- Data ownership -->
      <img src="https://storage.googleapis.com/diffgram_public/marketing/enterprise/Enterprise%20-%20your%20data%20your%20way.svg">

      <!-- Try for free -->
      <img src="https://storage.googleapis.com/diffgram_public/marketing/enterprise/Enterprise%20-%20try%20before%20buy.svg">

      <!-- Costs -->
      <img src="https://storage.googleapis.com/diffgram_public/marketing/enterprise/Enterprise%20-%20pricing.svg">

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
  name: 'enterprise_highlights',
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

