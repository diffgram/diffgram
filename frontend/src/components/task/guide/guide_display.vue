<template>
  <v-card v-if="guide">
    <v-card-title>{{guide.name}}</v-card-title>
    <v-card-text>
      <VueMarkDown :source="guide.markdown">
      </VueMarkDown>
    </v-card-text>
  </v-card>
  <v-card v-else class="d-flex justify-center align-center flex-column">
    <v-card-title><h1 class="font-weight-light">No Instructions to Show</h1></v-card-title>
    <v-icon size="350">mdi-book</v-icon>
  </v-card>

</template>

<script lang="ts">

  import Vue from "vue";
  
  export default Vue.extend( {
    name: 'guide_list',
    props: {
      'guide': {
        default: null
      }
    },

    data() {
      return {

      }
    },
    computed: {

    },
    mounted() {

    },
    methods: {

    }
  }

) </script>
