<template>
  <v-card bordered class="ma-2 pa-4 action-card" style="position: relative" @click="add_action_to_workflow">
    <v-chip
      v-if="is_trigger"
      x-small
      color="warning"
      style="position: absolute; top: -10px; right: -15px">
      <v-icon x-small>mdi-asterisk-circle-outline</v-icon>
      <strong>Trigger</strong>
    </v-chip>
    <div class="d-flex flex-column">
      <div class="d-flex">
        <div class="d-flex align-center mb-4">
          <v-img class="ma-2" width="50px" height="50px" :src="icon"></v-img>
          <div class="text-h6">{{ name }}</div>
        </div>

        <div>

        </div>
      </div>
      <div>
        <p class="font-weight-light text--primary lighten-1">{{description}}</p>
      </div>
    </div>

  </v-card>
</template>

<script>
export default {
  name: "action_step_box",
  props: ['node', 'name', 'description', 'icon', 'is_trigger'],
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
