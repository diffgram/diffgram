<template>
  <v-card class="pa-2">
    <v-card-title class="d-flex">
      {{title}}
      <div class="ml-auto">
        <div class="d-flex">
          <flowy-drag-handle>
            <v-btn small icon><v-icon>mdi-drag</v-icon></v-btn>
          </flowy-drag-handle>
        </div>
      </div>
    </v-card-title>
    <v-card-text>
      <div class="d-flex">

        <div class="q-py-md" v-html="description"/>

      </div>
    </v-card-text>

    <v-btn color="primary"  icon  x-small @click="remove"><v-icon color="red">mdi-delete</v-icon></v-btn>
  </v-card>
</template>

<script>
export default {
  name: "action_node_box",
  props: ['node', 'title', 'description', 'type', 'icon', 'remove'],
  methods: {

  }
}
</script>

<style scoped>

</style>
