<template>
  <v-card bordered class="ma-2 pa-4 d-flex">
    <div class="d-flex">
      <div>
        <div class="text-h6">{{ title }}</div>
      </div>

      <div>

      </div>
    </div>
    <div class="ml-auto">
      <flowy-drag-handle>
        <v-btn icon flat ><v-icon size="36">mdi-drag</v-icon></v-btn>
      </flowy-drag-handle>
    </div>
    <div class="q-py-md" v-html="description"/>
  </v-card>
</template>

<script>
import FlowyPlugin from "@hipsjs/flowy-vue";
import "@hipsjs/flowy-vue/dist/lib/flowy-vue.css";
export default {
  name: "action_step_box",
  props: ['remove', 'node', 'title', 'description'],
  methods: {
    remove: function(){
      this.$emit('remove')
    }
  }
}
</script>

<style scoped>

</style>
