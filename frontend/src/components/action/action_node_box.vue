<template>
  <div>
    <v-card :class="`pa-2 node-card ${kind === 'action_start' ? 'action-start' : ''}` "
            style="position: relative"
            @click="open_action_config">
      <v-chip
        v-if="is_trigger"
        x-small
        color="warning"
        style="position: absolute; top: -10px; right: -15px">
        <v-icon x-small>mdi-asterisk-circle-outline</v-icon>
        <strong>Trigger</strong>
      </v-chip>
      <v-card-title class="d-flex">
        <v-icon color="secondary" x-large>{{icon}}</v-icon>
        <strong>{{title}}</strong>
        <div class="ml-auto" v-if="kind !== 'action_start'" >
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

      <v-btn v-if="kind !== 'action_start'" color="primary"  icon  x-small @click="remove"><v-icon color="red">mdi-delete</v-icon></v-btn>
      <div v-if="is_last_node" class=" last-step-arrow d-flex flex-column justify-center align-center">
        <v-icon size="46">mdi-arrow-down</v-icon>
        <v-btn x-large icon color="secondary" ><v-icon>mdi-plus</v-icon></v-btn>
      </div>
    </v-card>
    <action_config_dialog ref="action_config_dialog" :action="node"></action_config_dialog>
  </div>

</template>

<script>
import action_config_dialog from "@/components/action/action_config_dialog";
export default {
  name: "action_node_box",
  components: {action_config_dialog},
  props: ['node', 'title', 'description', 'type', 'icon', 'remove', 'nodes', 'is_trigger', 'kind'],
  mounted() {
    console.log('MOUNTED DDDD', this.nodes)
  },
  methods: {
    open_action_config: function(){
      if(!this.$refs.action_config_dialog){
        return
      }
      this.$refs.action_config_dialog.open();
    },

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
.action-start{
  background: #efebe9 !important;
}
</style>
