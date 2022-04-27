<template>
  <div>
    <v-card :class="`pa-2 node-card ${action.kind === 'action_start' ? 'action-start' : ''}` "
            @click="select_action(action)"
            style="position: relative">
      <v-chip
        v-if="action.is_trigger"
        x-small
        color="warning"
        style="position: absolute; top: -10px; right: -15px">
        <v-icon x-small>mdi-asterisk-circle-outline</v-icon>
        <strong>Trigger</strong>
      </v-chip>
      <v-card-title class="d-flex">
        <v-icon style="width: 20%;" color="secondary" x-large>{{action.icon}}</v-icon>
        <strong style="width: 80%">{{action.title}}</strong>
<!--        <div style="width: 10%" class="ml-auto" v-if="action.kind !== 'action_start'" >-->
<!--          <div class="d-flex">-->
<!--            <flowy-drag-handle>-->
<!--              <v-btn small icon><v-icon>mdi-drag</v-icon></v-btn>-->
<!--            </flowy-drag-handle>-->
<!--          </div>-->
<!--        </div>-->
      </v-card-title>
      <v-card-text>
        <div class="d-flex">

          <div class="q-py-md" v-html="action.description"/>

        </div>
      </v-card-text>

      <v-btn v-if="action.kind !== 'action_start'" color="primary"  icon  x-small @click="remove"><v-icon color="red">mdi-delete</v-icon></v-btn>
      <div v-if="is_last_node" class=" last-step-arrow d-flex flex-column justify-center align-center">
        <v-icon size="46">mdi-arrow-down</v-icon>
        <v-btn @click="open_action_selector" x-large icon color="secondary" ><v-icon>mdi-plus</v-icon></v-btn>
      </div>
    </v-card>
    <action_selector_dialog
      @add_action_to_workflow="add_action_to_workflow"
      ref="action_selector_dialog"
      :action="node"></action_selector_dialog>

  </div>

</template>

<script>
import action_selector_dialog from "@/components/action/action_selector_dialog";

export default {
  name: "action_node_box",
  components: {
    action_selector_dialog,
  },
  props: ['node', 'action', 'actions_list'],
  mounted() {
    console.log('MOUNTED DDDD', this.nodes)
  },
  methods: {
    select_action: function(act){
      this.$emit('select_action', act)
    },
    add_action_to_workflow: function(act){
     this.$emit('add_action_to_workflow', act)
    },
    open_action_selector: function(){
      if(!this.$refs.action_selector_dialog){
        return
      }
      this.$refs.action_selector_dialog.open();
    },
    remove: function(){
      this.$emit('remove', this.action)
    }

  },
  computed: {
    is_last_node: function(){
      return this.actions_list.indexOf(this.action) === this.actions_list.length - 1
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
