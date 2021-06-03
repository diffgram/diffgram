<template>
  <v-container fluid>

  </v-container>
</template>

<script>
  import Vue from "vue";

  export default Vue.extend( {
    name: "model_run_selector",
    props:{
      project_string_id:{
        default: null
      },
      multi_select: {
        default: false
      },
      model_run_list: {
        default: false
      }

    }
  })
</script>

<style scoped>

</style>
