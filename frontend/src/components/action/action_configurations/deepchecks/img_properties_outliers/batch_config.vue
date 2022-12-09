<template>
  <div>
    <h4>Batch Size: </h4>
    <v-text-field
      v-model="action.config_data.batch_size"
      label="Batch Size"
      :rules="rules"
      hide-details="auto"
      @change="$emit('action_updated', action)"
    ></v-text-field>
  </div>
</template>

<script>


import {Action} from "@/components/action/Action";

export default {
  name: "batch_config",
  props:{
    action:{
      type: Action,
      required:true
    }
  },
  data: function(){
    return{
      rules: [
        value => !isNaN(value) || 'Must be a number',
      ]
    }
  },

  mounted() {
    if(!this.action.config_data.batch_size){
      this.action.config_data.batch_size = 1000
    }

  }
}
</script>

<style scoped>

</style>
