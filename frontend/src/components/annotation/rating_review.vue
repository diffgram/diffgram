<template>

  <div id="">

      <v-rating v-model="rating"
                medium
                class="nowrap"
                @input="$emit('rating_update', rating)"
                >
      </v-rating>


  </div>

</template>

<script lang="ts">

import axios from 'axios';


import Vue from "vue"; export default Vue.extend( {

  // not really sure if this needs to be it's own component...

  name: 'rating_review',
  props: ['rating_prop'],

  data () {
    return {

      rating: 3


    }
  },
  created() {
    // feels a bit akward
    this.rating = this.rating_prop
  },
  computed: {
  },
  methods: {

  }
}
) </script>
