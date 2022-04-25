<template>
  <v-card class="pa-2 node-card" style="position: relative">
    <v-card-title class="d-flex">
      <v-icon color="secondary" x-large>{{icon}}</v-icon>
      <strong>{{title}}</strong>
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
    <div v-if="is_last_node" class=" last-step-arrow d-flex flex-column justify-center align-center">
      <v-icon size="46">mdi-arrow-down</v-icon>
      <v-btn x-large icon color="secondary" ><v-icon>mdi-plus</v-icon></v-btn>
    </div>
  </v-card>
</template>

<script>
export default {
  name: "action_node_box",
  props: ['node', 'title', 'description', 'type', 'icon', 'remove', 'nodes'],
  mounted() {
    console.log('MOUNTED DDDD', this.nodes)
  },
  methods: {

  },
  computed: {
    is_last_node: function(){
      return this.nodes.indexOf(this.node) === this.nodes.length - 1
    }
  }
}
</script>

<style scoped>
.last-step-arrow {
  position: absolute;
  bottom: -100px;
  left: 40%;
}
.node-card:hover{
  background: #a1cdff;
  cursor: pointer;
  transition: 0.5s ease;
}
</style>
