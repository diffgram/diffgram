<template>
  <v-card bordered class="ma-2 pa-4" style="position: relative">
    <v-chip
      v-if="is_trigger"
      x-small
      color="warning"
      style="position: absolute; top: -10px; right: -15px">
      <v-icon x-small>mdi-asterisk-circle-outline</v-icon>
      <strong>Trigger</strong>
    </v-chip>
    <div class="d-flex">
      <div class="d-flex">
        <div class="d-flex align-center">
          <v-icon x-large color="secondary" class="mr-2">{{ icon }}</v-icon>
          <div class="text-h6">{{ title }}</div>
        </div>

        <div>

        </div>
      </div>
      <div class="ml-auto">
        <flowy-drag-handle>
          <v-btn icon ><v-icon size="36">mdi-drag</v-icon></v-btn>
        </flowy-drag-handle>
      </div>
      <div class="q-py-md" v-html="description"/>
    </div>

  </v-card>
</template>

<script>
export default {
  name: "action_step_box",
  props: ['node', 'title', 'description', 'icon', 'is_trigger'],
  methods: {
    remove: function(){
      this.$emit('remove')
    }
  }
}
</script>

<style scoped>

</style>
