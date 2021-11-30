<template>
<div id="pricing">

    <v-container>

    <v-card>
         <h1 class="pa-4"> Success </h1>

    <v-alert type="success">

      Welcome! You are on now the Premium plan!

    </v-alert>

    <v-btn color="primary"
            @click="$router.push('/home/dashboard')"
            block
            >
      Return Home
    </v-btn>
    
    </v-card>
 </v-container>


</div>
</template>

<script lang="ts">

import axios from 'axios';

import Vue from "vue";

export default Vue.extend( {
  name: 'order_success',
  components: {  },
  data () {
    return {

    }
  },
  created() {
  },
  computed: {
 

  },
  methods: {

  }
}
) </script>

