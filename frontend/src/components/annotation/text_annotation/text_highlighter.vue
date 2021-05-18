<template>
  <v-container>
    {{text}}
  </v-container>
</template>

<script>
  import Vue from "vue";

  export default Vue.extend({
    name: 'text_highlighter',
    props: ['text']
  })

</script>

<style scoped>

</style>
