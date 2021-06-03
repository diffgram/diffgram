<template>
  <div>
    <v-autocomplete
      dense
      v-model="current_run"
      :items="model_run_list"
    ></v-autocomplete>

  </div>
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

    },
    data: function(){
      return{
        current_run: undefined
      }
    }
  })
</script>

<style scoped>

</style>
