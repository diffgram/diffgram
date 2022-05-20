<template>
  <v-card bordered class="ma-2 pa-4 action-card" style="position: relative" @click="add_action_to_workflow">

    <div class="d-flex flex-column">
      <div class="d-flex">
        <div class="d-flex align-center mb-4">
          <v-img class="ma-2" width="50px" height="50px" :src="action.icon"></v-img>
          <div class="text-h6">{{ action.name }}</div>
        </div>

        <div>

        </div>
      </div>
      <div>
        <p class="font-weight-light text--primary lighten-1">{{action.description}}</p>
      </div>
    </div>

  </v-card>
</template>

<script>
export default {
  name: "action_step_box",
  props: ['action'],
  methods: {
    remove: function(){
      this.$emit('remove')
    },
    add_action_to_workflow: function(act){
      this.$emit('add_action_to_workflow', act)
    }
  }
}
</script>

<style scoped>
.action-card:hover{
  background: #a1cdff;
  cursor: pointer;
  transition: 0.5s ease;
}
</style>
